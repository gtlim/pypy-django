import datetime
import random
import string
import uuid
from collections import OrderedDict
from importlib import import_module

from django.conf import settings
from django.template.loader import render_to_string
from django.core.cache import cache
from django.db import models
from django.db.models import Max, Min
from django.db.models.aggregates import Count
from django.utils.text import slugify
from django.contrib.admindocs.utils import trim_docstring


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def pretty_slug(server):
    parts = server.split('.')
    if len(parts) == 3:
        return parts[1]
    return server


class ChatBotManager(models.Manager):
    def get_active_slugs(self):
        return [i[0] for i in
                self.get_queryset().filter(is_active=True).distinct(
                    'slug').values_list('slug')]


class NoAvailableChatBots(Exception):
    """
    Raised we we don't have any chat bots aviable that can be used on the network.
    """


class ChatBot(models.Model):
    is_active = models.BooleanField(default=False)

    server = models.CharField(
            max_length=100, help_text="Format: irc.example.net:6697")
    server_password = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            help_text="IRC server password - PASS command. Optional")
    server_identifier = models.CharField(max_length=164)

    nick = models.CharField(max_length=64)
    password = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            help_text="Password to identify with NickServ. Optional.")
    real_name = models.CharField(
            max_length=250,
            help_text="Usually a URL with information about this bot.")

    slug = models.CharField(max_length=50, db_index=True)
    max_channels = models.IntegerField(default=200)

    objects = ChatBotManager()

    @property
    def legacy_slug(self):
        return self.server.split(':')[0]

    def __unicode__(self):
        return u'{server} ({nick})'.format(server=self.server, nick=self.nick)

    @property
    def date_cache_key(self):
        return 'dc:{0}'.format(self.pk)

    def save(self, *args, **kwargs):
        self.server_identifier = u"%s.%s" % (
            slugify(unicode(self.server.replace(":", " ").replace(".", " "))),
            slugify(unicode(self.nick))
        )

        if not self.slug:
            server = self.server.split(':')[0]
            self.slug = pretty_slug(server)

        return super(ChatBot, self).save(*args, **kwargs)

    @classmethod
    def allocate_bot(cls, slug):
        bots = cls.objects.filter(slug='freenode', is_active=True).annotate(
            Count('channel')).order_by('channel__count')

        for bot in bots:
            if bot.max_channels > bot.channel__count:
                return bot
            else:
                continue

        raise NoAvailableChatBots(slug)


class ChannelQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(status=Channel.ACTIVE)


class ChannelManager(models.Manager):

    def get_queryset(self):
        return ChannelQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_queryset().filter(is_public=True)

    def active(self):
        self.get_queryset().active()


class Channel(TimeStampedModel):
    PENDING = 'PENDING'
    ACTIVE = 'ACTIVE'
    BANNED = 'BANNED'
    ARCHIVED = 'ARCHIVED'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived'),
        (BANNED, 'Banned')
    )

    # These are the default plugin slugs.
    DEFAULT_PLUGINS = ["logger", "ping", "last_seen", "help", "bangmotivate"]

    chatbot = models.ForeignKey(ChatBot)
    name = models.CharField(max_length=250,
                            help_text="IRC expects room name: #django")
    slug = models.SlugField()
    private_slug = models.SlugField(unique=True, blank=True, null=True,
                                    help_text="Slug used for private rooms")

    password = models.CharField(max_length=250, blank=True, null=True,
                                help_text="Password (mode +k) if the channel requires one")

    status = models.CharField(choices=STATUS_CHOICES, default=PENDING, max_length=20)

    # Flags
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    public_kudos = models.BooleanField(default=True)

    plugins = models.ManyToManyField('Plugin',
                                     through='ActivePlugin')

    fingerprint = models.CharField(max_length=36, blank=True, null=True)

    notes = models.TextField(blank=True)

    objects = ChannelManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        unique_together = (
            ('slug', 'chatbot'),
            ('name', 'chatbot')
        )

    @classmethod
    def generate_private_slug(cls):
        return "".join([random.choice(string.ascii_letters) for _ in xrange(8)])

    def get_absolute_url(self):
        from botbot.apps.bots.utils import reverse_channel
        return reverse_channel(self, 'log_current')

    def get_eventsource_url(self):
        from botbot.apps.bots.utils import reverse_channel
        return reverse_channel(self, 'log_stream')

    def create_default_plugins(self):
        """
        Adds our default plugins to the channel.
        :return:
        """
        for plugin in self.DEFAULT_PLUGINS:
            pobj = Plugin.objects.get(slug=plugin)
            active = ActivePlugin()
            active.plugin = pobj
            active.channel = self
            active.save()

    @property
    def active_plugin_slugs_cache_key(self):
        return 'channel:{0}:plugins'.format(self.name)

    def plugin_config_cache_key(self, slug):
        return 'channel:{0}:{1}:config'.format(self.name, slug)

    @property
    def active_plugin_slugs(self):
        """A cached set of the active plugins for the channel"""
        cache_key = self.active_plugin_slugs_cache_key
        cached_plugins = cache.get(cache_key)
        if not cached_plugins:
            plugins = self.activeplugin_set.all().select_related('plugin')
            slug_set = set([actv.plugin.slug for actv in plugins])
            cache.set(cache_key, slug_set)
            cached_plugins = slug_set
        return cached_plugins

    def plugin_config(self, plugin_slug):
        """A cached configuration for an active plugin"""
        cache_key = self.plugin_config_cache_key(plugin_slug)
        cached_config = cache.get(cache_key)
        if not cached_config:
            try:
                active_plugin = self.activeplugin_set.get(
                    plugin__slug=plugin_slug)
                cached_config = active_plugin.configuration
            except ActivePlugin.DoesNotExist:
                cached_config = {}
            cache.set(cache_key, cached_config)
        return cached_config

    def user_can_access_kudos(self, user):
        if self.public_kudos:
            return True
        return (
            user.is_authenticated()
        )

    @property
    def visible_commands_filter(self):
        """
        Provide Q object useful for limiting the logs to those that matter.
        Limits to certain IRC commands (including some more for
        private channels).
        """
        return models.Q(
            command__in=['PRIVMSG',
                         'NICK',
                         'NOTICE',
                         'TOPIC',
                         'ACTION',
                         'SHUTDOWN',
                         'JOIN',
                         'QUIT',
                         'PART',
                         'AWAY'
            ])

    def filtered_logs(self):
        return (self.log_set.filter(self.visible_commands_filter)
                            .exclude(command="NOTICE", nick="NickServ")
                            .exclude(command="NOTICE",
                                     text__startswith="*** "))

    def get_months_active(self):
        """
        Creates a OrderedDict of the format:
        {
            ...
            '2010': {
                first_day_of_month_datetime: pk_of_first_log,
                ...
            },
        }
        """
        current_month = datetime.datetime.today().month
        # Added the current month to the key to automatically update
        minmax_dict_key = "minmax_dict_%s_%s" % (self.id, current_month)
        minmax_dict = cache.get(minmax_dict_key, None)
        if minmax_dict is None:
            minmax_dict = self.log_set.all().aggregate(
                last_log=Max("timestamp"),
                first_log=Min("timestamp"))
            if not minmax_dict['first_log']:
                return OrderedDict()
            # cache for 10 days
            cache.set(minmax_dict_key, minmax_dict, 864000)
        first_log = minmax_dict['first_log'].date()
        last_log = minmax_dict['last_log'].date()
        last_log = datetime.date(last_log.year, last_log.month, 1)
        current = datetime.date(first_log.year, first_log.month, 1)
        months_active = OrderedDict()
        while current <= last_log:
            months_active.setdefault(current.year, []).append(current)
            if current.month == 12:
                current = datetime.date(current.year + 1, 1, 1)
            else:
                current = datetime.date(current.year, current.month + 1, 1)
        return months_active

    def current_size(self):
        """Number of users in this channel.
        We only log hourly, so can be a bit off.
        None if we don't have a record yet.
        """
        try:
            usercount = UserCount.objects.get(channel=self,
                                              dt=datetime.date.today())
        except UserCount.DoesNotExist:
            return None

        hour = datetime.datetime.now().hour

        try:
            # Postgres arrays are 1 based, but here become 0 based, so shift
            count = usercount.counts[hour - 2]
            if not count:
                # Try one hour ago in case not logged this hour yet
                count = usercount.counts[hour - 3]
        except IndexError:
            return None
        return count

    def save(self, *args, **kwargs):
        """
        Ensure that an empty slug is converted to a null slug so that it
        doesn't trip up on multiple slugs being empty.
        Update the 'fingerprint' on every save, its a UUID indicating the
        botbot-bot application that something has changed in this channel.
        """
        if not self.is_public and not self.private_slug:
            self.private_slug = self.generate_private_slug()

        self.fingerprint = uuid.uuid4()

        super(Channel, self).save(*args, **kwargs)


class Plugin(models.Model):
    """A global plugin registered in botbot"""
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    @property
    def user_docs(self):
        for mod_prefix in ('botbot_plugins.plugins.',
                           'botbot.apps.plugins.core.'):
            try:
                docs = import_module(mod_prefix + self.slug).Plugin.__doc__
                return trim_docstring(docs)
            except (ImportError, AttributeError):
                continue
        return ''

    def __unicode__(self):
        return self.name


class ActivePlugin(models.Model):
    """An active plugin for a ChatBot"""
    plugin = models.ForeignKey('Plugin')
    channel = models.ForeignKey('Channel')
    configuration = models.TextField(
            blank=True, default={},
            help_text="User-specified attributes for this plugin " +
            '{"username": "joe", "api-key": "foo"}')

    def save(self, *args, **kwargs):
        obj = super(ActivePlugin, self).save(*args, **kwargs)
        # Let the plugin_runner auto-reload the new values
        cache.delete(self.channel.plugin_config_cache_key(self.plugin.slug))
        cache.delete(self.channel.active_plugin_slugs_cache_key)
        return obj

    def __unicode__(self):
        return u'{0} for {1}'.format(self.plugin.name, self.channel.name)


class UserCount(models.Model):
    """Number of users in a channel, per hour."""

    channel = models.ForeignKey(Channel)
    dt = models.DateField()
    counts = models.IntegerField()

    def __unicode__(self):
        return "{} on {}: {}".format(self.channel, self.dt, self.counts)

REDACTED_TEXT = '[redacted]'

MSG_TMPL = {
        u"JOIN": u"{nick} joined the channel",
        u"NICK": u"{nick} is now known as {text}",
        u"QUIT": u"{nick} has quit",
        u"PART": u"{nick} has left the channel",
        u"ACTION": u"{nick} {text}",
        u"SHUTDOWN": u"-- BotBot disconnected, possible missing messages --",
        }


class Log(models.Model):
    bot = models.ForeignKey('ChatBot', null=True)
    channel = models.ForeignKey('Channel', null=True)
    timestamp = models.DateTimeField(db_index=True)
    nick = models.CharField(max_length=255)
    text = models.TextField()
    action = models.BooleanField(default=False)

    command = models.CharField(max_length=50, null=True, blank=True)
    host = models.TextField(null=True, blank=True)
    raw = models.TextField(null=True, blank=True)

    # freenode chan name length limit is 50 chars, Campfire room ids are ints,
    #  so 100 should be enough
    room = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('-timestamp',)
        index_together = [
            ['channel', 'timestamp'],
        ]

    def get_absolute_url(self):
        return "TODO"

    def as_html(self):
        return render_to_string("logs/log_display.html",
                                {'message_list': [self]})
    def get_cleaned_host(self):
        if self.host:
            if '@' in self.host:
                return self.host.split('@')[1]
            else:
                return self.host

    def get_nick_color(self):
        return hash(self.nick) % 32

    def __unicode__(self):
        if self.command == u"PRIVMSG":
            text = u''
            if self.nick:
                text += u'{0}: '.format(self.nick)
            text += self.text[:20]
        else:
            try:
                text = MSG_TMPL[self.command].format(nick=self.nick, text=self.text)
            except KeyError:
                text = u"{}: {}".format(self.command, self.text)

        return text

    def save(self, *args, **kwargs):
        if self.nick in settings.EXCLUDE_NICKS:
            self.text = REDACTED_TEXT

        obj = super(Log, self).save(*args, **kwargs)
        return obj

import inspect
import datetime

from django_perf_project.apps.core.tests import PerfoTestCase

from .models import Channel, ChatBot


class BotbotPerfoTest(PerfoTestCase):

    def setUp(self):
        super(BotbotPerfoTest, self).setUp()

        self.start_date = datetime.date(2015, 4, 1)
        self.next_day = self.start_date + datetime.timedelta(days=1)
        self.previous_day = self.start_date - datetime.timedelta(days=1)
        self.slug = 'pypy'

        chatbot = ChatBot.objects.create(
            is_active=True, server="irc.example.net:6697",
            nick="foo", password="bar",slug="thechatbot")
        Channel.objects.create(
            chatbot=chatbot,
            status=Channel.ACTIVE,
            slug=self.slug,
            is_public=True)

    def test_reduced_botbot_logs(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            channel = (Channel.objects.filter(status=Channel.ACTIVE,
                                              slug=self.slug,
                                              is_public=True)
                                      .select_related('chatbot'))[0]
            size = channel.current_size()
            # current logs
            logs = (channel.filtered_logs()
                           .filter(timestamp__gte=self.start_date,
                                   timestamp__lt=self.next_day)
                           .order_by('timestamp'))
            # determine page number of previous logs
            prev_count = (channel.filtered_logs()
                                 .filter( timestamp__gte=self.previous_day,
                                         timestamp__lt=self.start_date)
                                 .order_by('timestamp').count())

            # determine next page number
            next_count = logs.count()
            if size:
                print("Members: {}".format(size))
            return {
                'logs': list(logs),
                'prev_count': prev_count,
                'next_count': next_count}

        self.run_benchmark(name, self.small_iterations, f)

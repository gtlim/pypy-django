import inspect
import datetime

import populate
from django_perf_project.apps.core.tests import PerfoTestCase

from .models import Channel, ChatBot


def simulate_botbot_queries(slug, start_date):
    next_day = start_date + datetime.timedelta(days=1)
    previous_day = start_date - datetime.timedelta(days=1)

    channel = (Channel.objects.filter(status=Channel.ACTIVE,
                                      slug=slug,
                                      is_public=True)
                              .select_related('chatbot'))[0]
    size = channel.current_size()
    # current logs
    logs = (channel.filtered_logs()
                   .filter(timestamp__gte=start_date,
                           timestamp__lt=next_day)
                   .order_by('timestamp'))
    # determine page number of previous logs
    prev_count = (channel.filtered_logs()
                         .filter(timestamp__gte=previous_day,
                                 timestamp__lt=start_date)
                         .order_by('timestamp').count())

    # determine next page number
    next_count = logs.count()
    if size:
        print("Members: {}".format(size))
    return {
        'logs': list(logs),
        'prev_count': prev_count,
        'next_count': next_count}


class EmptyBotbotPerfoTest(PerfoTestCase):

    def setUp(self):
        super(EmptyBotbotPerfoTest, self).setUp()

        self.start_date = datetime.date(2015, 4, 1)
        self.slug = 'pypy'

        chatbot = ChatBot.objects.create(
            is_active=True, server="irc.example.net:6697",
            nick="foo", password="bar", slug="thechatbot")
        Channel.objects.create(
            chatbot=chatbot,
            status=Channel.ACTIVE,
            slug=self.slug,
            is_public=True)

    def test_reduced_botbot_logs(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            simulate_botbot_queries(self.slug, self.start_date)

        self.run_benchmark(name, self.small_iterations, f)


class LoadedBotbotPerfoTest(PerfoTestCase):

    def setUp(self):
        super(LoadedBotbotPerfoTest, self).setUp()

        self.start_date = datetime.date(2015, 4, 1)
        self.slug = 'pypy'
        populate.populate_botbot(self.slug, self.start_date)

    def test_reduced_botbot_logs(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            simulate_botbot_queries(self.slug, self.start_date)

        self.run_benchmark(name, self.xsmall_iterations, f)


import os, sys

#import tracer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_perf_project.settings')
import django
django.setup()

import datetime
from django.utils.timezone import utc
from django_perf_project.apps.botbotperf.models import Channel, ChatBot

chatbot = ChatBot.objects.create(
            is_active=True, server="irc.example.net:6697",
            nick="foo", password="bar",slug="thechatbot")
Channel.objects.create(
            chatbot=chatbot,
            status=Channel.ACTIVE,
            slug='pypy',
            is_public=True)
def f():
    channel = (Channel.objects.filter(status=Channel.ACTIVE,
                                      slug='pypy',
                                      is_public=True)
                              .select_related('chatbot'))[0]
    size = channel.current_size()
    # current logs
    start_date = datetime.datetime(2015, 4, 1, tzinfo=utc)
    next_day = start_date + datetime.timedelta(days=1)
    previous_day = start_date - datetime.timedelta(days=1)

    logs = (channel.filtered_logs()
                   .filter(timestamp__gte=start_date,
                           timestamp__lt=next_day)
                   .order_by('timestamp'))
    # determine page number of previous logs
    prev_count = (channel.filtered_logs()
                         .filter( timestamp__gte=previous_day,
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

import time
for k in range(300):
    t0 = time.time()
    for k in range(100):
        f()
    print time.time() - t0

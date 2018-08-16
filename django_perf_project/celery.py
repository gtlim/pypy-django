# -*- coding: utf-8 -*-
from __future__ import absolute_import
import urllib2
import os
from collections import defaultdict
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_perf_project.settings')

from celery import Celery
app = Celery('django_perf_project')
app.config_from_object('django.conf:settings')

from django_perf_project.apps.botbotperf.models import Channel, ChatBot
import time
import datetime
from django.utils.timezone import utc

class Box(object):
    def __init__(self):
        self.counter = 0
    def something(self):
        self.counter += 1
        if self.counter > 100:
            self.counter = 0

@app.task
def edgeworker_run():
    t0 = time.time()
    boxes = []
    for i in range(10000000):
        boxes.append(Box())

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
    print time.time() - t0
    return None
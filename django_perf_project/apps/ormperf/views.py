from django.shortcuts import render

# Create your views here.
import datetime
from django.utils.timezone import utc
from django_perf_project.apps.botbotperf.models import Channel, ChatBot
from django_perf_project.celery import edgeworker_run
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
import time

index = 0

from functools import wraps
import os
import vmprof
# '/sendbird/jitlogs/'+ args[2] + time.strftime('%Y-%m-%d-%H-%M-%S') + 'prof.jitlog'
def prof(f):
    @wraps(f)
    def f_prof(*args, **kwargs):
      global index
      index += 1
      if index % 100 == 0:
          _profiler_fd = os.open(
            '/pypy-django/jitlogs/'+  f.__name__ +'_'+ time.strftime('%Y-%m-%d-%H-%M-%S') +'_prof.jitlog',
            os.O_RDWR | os.O_CREAT | os.O_TRUNC
          )
          try:
            vmprof.enable(_profiler_fd)
          except:
            pass
          val = f(*args, **kwargs)
          vmprof.disable()
          os.close(_profiler_fd)
          return val
      else:
          val = f(*args, **kwargs)
          return  val
    return f_prof  # true decorator






@require_http_methods(["GET"])
@prof
def f(request):
    edgeworker_run.apply_async()
    return HttpResponse(status=201)
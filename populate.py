
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_perf_project.settings')
import django
django.setup()

from django.utils import timezone
from ormperf.models import Question, Choice
from datetime import datetime, timedelta

if __name__ == '__main__':
    d0 = timezone.datetime(2015, 10, 21, tzinfo=timezone.utc)
    for i in range(1000):
        q = Question(question_text="foo bar %d" % i, pub_date=d0 + timedelta(seconds=i))
        q.save()
        for k in range(3):
            c = Choice(question=q, choice_text="aaaaaaaaaaaa %d %d" % (i, k), votes=i)
            c.save()

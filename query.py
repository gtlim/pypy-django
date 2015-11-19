
import os, sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_perf_test.settings')
import django
django.setup()

from fooapp.models import Question, Choice
from datetime import datetime, timedelta
from django.utils.timezone import utc

def main():
    d0 = datetime(2015, 10, 21, 0, 0, 15, tzinfo=utc)
    d1 = datetime(2015, 10, 21, 0, 0, 30, tzinfo=utc)
    for i in xrange(int(sys.argv[1])):
        # make sure we exhaust the iterators
        [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]

if __name__ == '__main__':
    main()

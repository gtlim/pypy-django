import time
from datetime import datetime
from django.test import TestCase
from django.utils.timezone import utc

from fooapp.models import Question

class PerfoTest(TestCase):

    def setUp(self): 
        self.iterations = 1000

    def test_orm_datetime_filtering(self):
        name = "orm_datetime_filtering"
        d0 = datetime(2015, 10, 21, 0, 0, 15, tzinfo=utc)
        d1 = datetime(2015, 10, 21, 0, 0, 30, tzinfo=utc)
        start = time.time()
        for i in xrange(10):
            # make sure we exhaust the iterators
            [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]
        duration = time.time() - start
        print u"{0}s per iteration for {1}".format(duration/self.iterations, name)



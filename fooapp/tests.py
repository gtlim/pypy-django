import time
from datetime import datetime
from django.test import TestCase
from django.utils.timezone import utc

from fooapp.models import Question

class PerfoTest(TestCase):

    def setUp(self): 
        pass


    def test_datetime(self):
        t0 = time.time()
        d0 = datetime(2015, 10, 21, 0, 0, 15, tzinfo=utc)
        d1 = datetime(2015, 10, 21, 0, 0, 30, tzinfo=utc)
        for i in xrange(10):
            # make sure we exhaust the iterators
            [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]
        print time.time() - t0
    



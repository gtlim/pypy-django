import inspect
import time
from datetime import datetime
from django.test import TestCase
from django.utils.timezone import utc

from fooapp.models import Question


def add(x, y):
    return x + y


class PerfoTest(TestCase):

    def setUp(self):
        self.iterations = 100000
        # creating 100 questions
        for i in range(10):
            Question.objects.create(
                question_text="q {}".format(i),
                pub_date=datetime(2015, 10, 21, i, 0, 15, tzinfo=utc))

    def test_int_addition(self):
        """
        add 2 int

        This test is a sanity check to confirm that pypy is sometimes faster
        """
        name = inspect.currentframe().f_code.co_name[5:]
        start = time.time()
        for i in xrange(10):
            add(1, 2)
        duration = time.time() - start
        print u"{0}s per iteration for {1} (iterations={2})".format(duration/self.iterations, name, self.iterations)

    def test_orm_datetime_filtering(self):
        name = inspect.currentframe().f_code.co_name[5:]
        d0 = datetime(2015, 10, 21, 0, 0, 15, tzinfo=utc)
        d1 = datetime(2015, 10, 21, 0, 0, 30, tzinfo=utc)
        start = time.time()
        for i in xrange(10):
            # make sure we exhaust the iterators
            [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]
        duration = time.time() - start
        print u"{0}s per iteration for {1} (iterations={2})".format(duration/self.iterations, name, self.iterations)

import inspect
import time
from datetime import datetime

from django.db.models import Count
from django.test import TestCase
from django.utils.timezone import utc

from fooapp.models import Question


def add(x, y):
    return x + y


class PerfoTest(TestCase):

    def setUp(self):
        self.iterations = [1, 10, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7]
        self.small_iterations = self.iterations[0:6]

        # creating 100 questions
        for i in range(1, 11):
            for j in range(10):
                Question.objects.create(
                    question_text="q {}".format(i),
                    pub_date=datetime(2015, 10, i, j, 0, 15, tzinfo=utc))

    def report_run(self, name, nb_iteration,
                   total_duration, last_iteration_duration):
        print u"{0:e}s per iteration for {1} (iterations={2}) -- last operation: {3:e}s".format(total_duration/nb_iteration, name, nb_iteration, last_iteration_duration)

#    def test_is_pypyjit_available(self):
#        try:
#            import pypyjit
#            snp=pypyjit.get_stats_snapshot()
#            print u"pypyjit.get_stats_snapshot().counter_times: {}".format(snp.counter_times)
#        except ImportError:
#            self.assertEqual(True, False, "pypyjit is not available")

    def test_int_addition(self):
        """
        add 2 int

        This test is a sanity check to confirm that pypy is sometimes faster
        """
        name = inspect.currentframe().f_code.co_name[5:]
        print
        for n in self.iterations:
            start = time.time()
            for i in xrange(int(n)):
                add(1, 2)
            duration = time.time() - start
            start = time.time()
            add(1, 2)
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)

    def test_orm_datetime_filtering(self):
        name = inspect.currentframe().f_code.co_name[5:]
        d0 = datetime(2015, 10, 1, 0, 0, 0, tzinfo=utc)
        d1 = datetime(2015, 10, 12, 10, 0, 0, tzinfo=utc)
        print
        for n in self.small_iterations:
            start = time.time()
            for i in xrange(int(n)):
                # make sure we exhaust the iterators
                [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]
            duration = time.time() - start
            start = time.time()
            [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)

    def test_orm_first_ten(self):
        name = inspect.currentframe().f_code.co_name[5:]
        print
        for n in self.small_iterations:
            start = time.time()
            for i in xrange(int(n)):
                # make sure we exhaust the iterators
                [x for x in Question.objects.all()[:10]]
            duration = time.time() - start
            start = time.time()
            [x for x in Question.objects.all()[:10]]
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)

    def test_orm_annotation(self):
        name = inspect.currentframe().f_code.co_name[5:]
        print
        for n in self.small_iterations:
            start = time.time()
            for i in xrange(int(n)):
                # make sure we exhaust the iterators
                [q for q in Question.objects.extra({'pub_day':"date(pub_date)"}).values('pub_day').annotate(count=Count('id'))]
            duration = time.time() - start
            start = time.time()
            [q for q in Question.objects.extra({'pub_day':"date(pub_date)"}).values('pub_day').annotate(count=Count('id'))]
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)



#    def test_template_rendering(self):
#        name = inspect.currentframe().f_code.co_name[5:]


import inspect
from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.utils.timezone import utc

from .models import Question
from django_perf_project.apps.core.tests import PerfoTestCase


def add(x, y):
    return x + y


class OrmPerfoTest(PerfoTestCase):

    def setUp(self):
        super(OrmPerfoTest, self).setUp()

        # creating 100 questions
        for i in range(1, 11):
            for j in range(10):
                Question.objects.create(
                    question_text="q {}".format(i),
                    pub_date=datetime(2015, 10, i, j, 0, 15, tzinfo=utc))

    def test_is_pypyjit_available(self):
        try:
            import pypyjit
            snp=pypyjit.get_stats_snapshot()
            print u"pypyjit.get_stats_snapshot().counter_times: {}".format(snp.counter_times)
        except ImportError:
            self.assertEqual(True, False, "pypyjit is not available")


    def test_int_addition(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            return add(1, 2)
        self.run_benchmark(name, self.iterations, f)

    def test_orm_datetime_filtering(self):
        name = inspect.currentframe().f_code.co_name[5:]
        d0 = datetime(2015, 10, 1, 0, 0, 0, tzinfo=utc)
        d1 = datetime(2015, 10, 12, 10, 0, 0, tzinfo=utc)

        def f():
            return [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]
        self.run_benchmark(name, self.small_iterations, f)

    def test_orm_first_ten(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            return [x for x in Question.objects.all()[:10]]
        self.run_benchmark(name, self.small_iterations, f)

    def test_orm_annotation(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f ():
            return [q for q in Question.objects.extra({'pub_day': "date(pub_date)"}).values('pub_day').annotate(count=Count('id'))]
        self.run_benchmark(name, self.small_iterations, f)

    def test_orm_clone(self):
        name = inspect.currentframe().f_code.co_name[5:]
        d0 = datetime(2015, 10, 1, 0, 0, 0, tzinfo=utc)
        d1 = d0 + timedelta(days=1)

        def f():
            qs = Question.objects.all()
            qs = qs.filter(pub_date__gte=d0)
            qs = qs.filter(pub_date__lt=d1)
            return [x for x in qs]
        self.run_benchmark(name, self.small_iterations, f)

    def test_orm_or_q(self):
        name = inspect.currentframe().f_code.co_name[5:]
        d0 = datetime(2015, 10, 1, 0, 0, 0, tzinfo=utc)
        d1 = d0 + timedelta(days=1)
        d2 = d1 + timedelta(days=1)
        d3 = d2 + timedelta(days=1)
        d4 = d3 + timedelta(days=1)
        d5 = d4 + timedelta(days=1)
        d6 = d5 + timedelta(days=1)
        d7 = d6 + timedelta(days=1)

        q1 = Q(pub_date__gte=d0, pub_date__lt=d1)
        q2 = Q(pub_date__gte=d1, pub_date__lt=d2)
        q3 = Q(pub_date__gte=d3, pub_date__lt=d4)
        q4 = Q(pub_date__gte=d4, pub_date__lt=d5)
        q5 = Q(pub_date__gte=d6, pub_date__lt=d7)

        def f():
            qs = Question.objects.filter(q1 | q2 | q3 | q4 | q5)
            return [x for x in qs]
        self.run_benchmark(name, self.small_iterations, f)

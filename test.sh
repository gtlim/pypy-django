#!/usr/bin/env bash

pip install . -r requirements.txt -q
#python manage.py test

# python manage.py test django_perf_project.apps.ormperf.tests.OrmPerfoTest.test_int_addition
python manage.py test django_perf_project.apps.ormperf.tests.OrmPerfoTest.test_orm_datetime_filtering
# python manage.py test django_perf_project.apps.ormperf.tests.OrmPerfoTest.test_orm_first_ten
# python manage.py test django_perf_project.apps.ormperf.tests.OrmPerfoTest.test_orm_annotation
# python manage.py test django_perf_project.apps.ormperf.tests.OrmPerfoTest.test_orm_clone
# python manage.py test django_perf_project.apps.ormperf.tests.OrmPerfoTest.test_orm_or_q
# python manage.py test django_perf_project.apps.templateperf.tests.TemplatePerfTest.test_render_child
# python manage.py test django_perf_project.apps.templateperf.tests.TemplatePerfTest.test_render_child_no_extends
python manage.py test django_perf_project.apps.templateperf.tests.TemplatePerfTest.test_render_base
# python manage.py test django_perf_project.apps.templateperf.tests.TemplatePerfTest.test_render_base_no_extends
python manage.py test django_perf_project.apps.botbotperf.tests.EmptyBotbotPerfoTest.test_reduced_botbot_logs
# python manage.py test django_perf_project.apps.botbotperf.tests.LoadedBotbotPerfoTest.test_reduced_botbot_logs
# python manage.py test django_perf_project.apps.ormperf.tests.OrmPerfoTest.test_is_pypyjit_available


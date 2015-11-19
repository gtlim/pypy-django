#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-perf-tester',
    version='0.0.1',
    description="",
    url='',
    packages=find_packages(),
    package_data={'perf_tester': ['static/*.*', 'templates/*.*']},
    scripts=['manage.py', 'query.py'],
)

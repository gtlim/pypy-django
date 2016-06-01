#!/usr/bin/env bash

set -ex

docker rm django-perf; docker run -t --name=django-perf  -v "$PWD":/usr/src/django-perf -w /usr/src/django-perf pypy:2-5.1.1 bash -c "ln -sf /usr/local/bin/pypy /usr/local/bin/python; bash test.sh" > result_test_pypy.txt
docker rm django-perf; docker run -t --name=django-perf  -v "$PWD":/usr/src/django-perf -w /usr/src/django-perf python:2.7.11 bash test.sh > result_test_python2.7.11.txt
docker rm django-perf; docker run -t --name=django-perf  -v "$PWD":/usr/src/django-perf -w /usr/src/django-perf pyston/pyston bash test.sh > result_test_pyston.txt

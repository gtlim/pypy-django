# django-perf-tester

The goal of this project is to benchmark pypy against python 2.7

## Installation

* Create a virtualenv `virtualenv -p /usr/bin/pypy pypy_venv`
* cd into this new virtualenv and activate it`. bin/activate`
* `pip install -e git+https://github.com/yml/django-perf-tester#egg=django-perf-tester`
* pip install the requirements `pip install -r src/django-perf-tester/requirements.txt`
* run `tox -c src/django-perf-tester/tox.ini`

#!/usr/bin/env python
import sys
from os.path import dirname, abspath
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        USE_TZ=True,
        GOCARDLESS_APP_SECRET=(
            'BBYKKNKEK4WKN9YVK0BRARGS4QHDRVJB8J'
            'WYM84XTR9XQ591RGFSEFQ82B0ZKKYM'),
        ROOT_URLCONF='django_gocardless.webhook.urls',
        INSTALLED_APPS=[
            'django_gocardless.webhook',
        ],
        NOSE_ARGS = [
            '--with-coverage',
            '--cover-package=django_gocardless'
        ]
    )

parent = dirname(abspath(__file__))
sys.path.insert(0, parent)

from django_nose import NoseTestSuiteRunner
test_runner = NoseTestSuiteRunner(verbosity=1)

failures = test_runner.run_tests(['django_gocardless', ])
if failures:
    sys.exit(failures)

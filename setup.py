#!/usr/bin/env python

from setuptools import setup, find_packages

import django_gocardless

setup(
    name='django-gocardless',
    version=".".join(map(str, django_gocardless.__version__)),
    author='Ben Mason',
    author_email='ben@sharkbyte.co.uk',
    maintainer="Ben Mason",
    maintainer_email="ben@sharkbyte.co.uk",
    url='http://github.com/astonecutter/django-cardless',
    install_requires=[
        'Django>=1.0',
        'gocardless',
        'django_model_utils',
        'django-nose'
    ],
    description=(
        'A pluggable Django application for integrating GoCardless payments'),
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)

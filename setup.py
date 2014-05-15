#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup, find_packages


setup(
    name='django-resize',
    description='Simple Django Image Resizing',
    url='http://github.com/defrex/django-resize/',
    license='MIT',
    author='Aron Jones',
    author_email='aron.jones@gmail.com',
    packages=find_packages(),
    version='0.1.0',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django>=1.5',
    ],
)

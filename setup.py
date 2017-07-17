#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 SeatGeek

# This file is part of haldane.

from app import __version__
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


def run_setup():
    setup(
        name='haldane',
        version=__version__,
        description='A friendly http interface to the aws api',
        keywords='aws api',
        url='https://github.com/seatgeek/haldane',
        author='SeatGeek',
        author_email='opensource@seatgeek.com',
        license='BSD',
        packages=['app'],
        install_requires=open_file('requirements.txt').readlines(),
        test_suite='tests',
        long_description=open_file('README.rst').read(),
        include_package_data=True,
        zip_safe=True,
        classifiers=[
        ],
    )

if __name__ == '__main__':
    run_setup()

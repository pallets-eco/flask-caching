#!/usr/bin/env python
"""
Flask-Caching
-------------

Adds cache support to your Flask application

"""

from setuptools import setup

setup(
    name='Flask-Caching',
    version='0.13',
    url='https://github.com/sh4nks/flask-caching',
    license='BSD',
    author='Peter Justin',
    author_email='Peter Justin',
    description='Adds caching support to your Flask application',
    long_description=__doc__,
    packages=[
        'flask_caching',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    test_suite='test_cache',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

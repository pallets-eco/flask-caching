#!/usr/bin/env python
"""
Flask-Caching
=============

Adds easy cache support to Flask.

Setup
-----

The Cache Extension can either be initialized directly:

.. code:: python

    from flask import Flask
    from flask_caching import Cache

    app = Flask(__name__)
    # For more configuration options, check out the documentation
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

Or through the factory method:

.. code:: python

    cache = Cache(config={'CACHE_TYPE': 'simple'})

    app = Flask(__name__)
    cache.init_app(app)

Links
=====

* `Documentation <https://pythonhosted.org/Flask-Caching/>`_
* `Source Code <https://github.com/sh4nks/flask-caching>`_
* `Issues <https://github.com/sh4nks/flask-caching/issues>`_
* `original Flask-Cache Extension <https://github.com/thadeusb/flask-cache>`_

"""
import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('flask_caching/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='Flask-Caching',
    version=version,
    url='https://github.com/sh4nks/flask-caching',
    license='BSD',
    author='Peter Justin',
    author_email='Peter Justin',
    description='Adds caching support to your Flask application',
    long_description=__doc__,
    packages=['flask_caching'],
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
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

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
    cache = Cache(app, config={"CACHE_TYPE": "simple"})

Or through the factory method:

.. code:: python

    cache = Cache(config={"CACHE_TYPE": "simple"})

    app = Flask(__name__)
    cache.init_app(app)

Links
=====

* `Documentation <https://flask-caching.readthedocs.io>`_
* `Source Code <https://github.com/sh4nks/flask-caching>`_
* `Issues <https://github.com/sh4nks/flask-caching/issues>`_
* `original Flask-Cache Extension <https://github.com/thadeusb/flask-cache>`_

"""
import ast
import re

from setuptools import find_packages, setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("flask_caching/__init__.py", "rb") as f:
    content = f.read().decode("utf-8")
    version = str(
        ast.literal_eval(_version_re.search(content).group(1))  # type: ignore
    )


setup(
    name="Flask-Caching",
    version=version,
    url="https://github.com/sh4nks/flask-caching",
    license="BSD",
    author="Peter Justin",
    author_email="peter.justin@outlook.com",
    description="Adds caching support to your Flask application",
    long_description=__doc__,
    packages=find_packages(exclude=("tests",)),
    zip_safe=False,
    platforms="any",
    python_requires=">=3.5",
    install_requires=["Flask"],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-xprocess",
        "pylibmc",
        "redis",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
)

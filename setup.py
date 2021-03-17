#!/usr/bin/env python
import os
import ast
import re

from setuptools import find_packages, setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


version_line = re.search(
    r"__version__\s+=\s+(.*)", read("flask_caching", "__init__.py")
).group(1)

version = str(ast.literal_eval(version_line))
long_description = read("README.md")


setup(
    name="Flask-Caching",
    version=version,
    project_urls={
        "Documentation": "https://flask-caching.readthedocs.io",
        "Source Code": "https://github.com/sh4nks/flask-caching",
        "Issue Tracker": "https://github.com/sh4nks/flask-caching",
    },
    url="https://github.com/sh4nks/flask-caching",
    license="BSD",
    author="Peter Justin",
    author_email="peter.justin@outlook.com",
    description="Adds caching support to your Flask application",
    long_description=long_description,
    long_description_content_type="text/markdown",
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

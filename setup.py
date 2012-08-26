#!/usr/bin/env python
"""
Flask-Cache
-----------

Adds cache support to your Flask application

"""
from flaskext.cache import __version__

from setuptools import setup

setup(
    name='Flask-Cache',
    version=__version__,
    url='http://github.com/thadeusb/flask-cache',
    license='BSD',
    author='Thadeus Burgess',
    author_email='thadeusb@thadeusb.com',
    description='Adds cache support to your Flask application',
    long_description=__doc__,
    packages=[
        'flaskext',
        'flaskext.cache',
    ],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'setuptools',
        'Flask',
    ],
    test_suite='test_cache',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

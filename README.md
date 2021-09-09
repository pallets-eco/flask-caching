Flask-Caching
=============

[![Build Status](https://github.com/sh4nks/flask-caching/actions/workflows/tests.yml/badge.svg)](https://github.com/sh4nks/flask-caching/actions)
[![codecov](https://codecov.io/gh/sh4nks/flask-caching/branch/master/graph/badge.svg?token=6Cp6Y0BitB)](https://codecov.io/gh/sh4nks/flask-caching)
[![PyPI Version](https://img.shields.io/pypi/v/Flask-Caching.svg)](https://pypi.python.org/pypi/Flask-Caching)
[![Documentation Status](https://readthedocs.org/projects/flask-caching/badge/?version=latest)](https://flask-caching.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/license-BSD-yellow.svg)](https://github.com/sh4nks/flask-caching)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Adds easy cache support to Flask.

This is a fork of the [Flask-Cache](https://github.com/thadeusb/flask-cache)
extension.

Flask-Caching also includes the ``cache`` module from werkzeug licensed under a
BSD-3 Clause License.


Setup
-----

Flask-Caching is available on PyPI and can be installed with:

    pip install flask-caching

The Cache Extension can either be initialized directly:

```python
from flask import Flask
from flask_caching import Cache

app = Flask(__name__)
# For more configuration options, check out the documentation
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
```

Or through the factory method:

```python
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)
cache.init_app(app)
```

Compatibility with Flask-Cache
-----
There are no known incompatibilities or breaking changes between the latest [Flask-Cache](https://github.com/thadeusb/flask-cache)
release (version 0.13, April 2014) and the current version of Flask-Caching. Due to the change to the Flask-Caching name
and the [extension import transition](http://flask.pocoo.org/docs/0.11/extensiondev/#extension-import-transition),
Python import lines like:

 ```from flask.ext.cache import Cache```

 will need to be changed to:

 ```from flask_caching import Cache```

Python versions
-----

Starting with version 1.8, Flask-Caching dropped Python 2 support. The library is tested against Python 3.6, 3.7, 3.8, 3.9 and PyPy 3.6.

Links
=====

* [Documentation](https://flask-caching.readthedocs.io)
* [Source Code](https://github.com/sh4nks/flask-caching)
* [Issues](https://github.com/sh4nks/flask-caching/issues)
* [Original Flask-Cache Extension](https://github.com/thadeusb/flask-cache)

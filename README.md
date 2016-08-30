Flask-Caching
=============

[![Build Status](https://travis-ci.org/sh4nks/flask-caching.svg?branch=master)](https://travis-ci.org/sh4nks/flask-caching)
[![Coverage Status](https://coveralls.io/repos/sh4nks/flask-caching/badge.png)](https://coveralls.io/r/sh4nks/flask-caching)
[![PyPI Version](https://img.shields.io/pypi/v/Flask-Caching.svg)](https://pypi.python.org/pypi/Flask-Caching)
[![License](https://img.shields.io/badge/license-BSD-yellow.svg)](https://github.com/sh4nks/flask-caching)

Adds easy cache support to Flask.

This is a fork of the [Flask-Cache](https://github.com/thadeusb/flask-cache)
extension.


Setup
-----

The Cache Extension can either be initialized directly:

```python
from flask import Flask
from flask_caching import Cache

app = Flask(__name__)
# For more configuration options, check out the documentation
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

Or through the factory method:

```python
cache = Cache(config={'CACHE_TYPE': 'simple'})

app = Flask(__name__)
cache.init_app(app)
```


Links
=====

* [Documentation](https://pythonhosted.org/Flask-Caching/)
* [Source Code](https://github.com/sh4nks/flask-caching)
* [Issues](https://github.com/sh4nks/flask-caching/issues)
* [Original Flask-Cache Extension](https://github.com/thadeusb/flask-cache)

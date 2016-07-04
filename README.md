Flask-Caching
=============

[![Build Status](https://travis-ci.org/sh4nks/flask-caching.svg?branch=master)](https://travis-ci.org/sh4nks/flask-caching)
[![Coverage Status](https://coveralls.io/repos/sh4nks/flask-caching/badge.png)](https://coveralls.io/r/sh4nks/flask-caching)
[![PyPI Version](https://img.shields.io/pypi/v/Flask-Caching.svg)](https://pypi.python.org/pypi/Flask-Caching)
[![License](https://img.shields.io/badge/license-BSD-yellow.svg)](https://github.com/sh4nks/flask-caching)

Adds easy cache support to Flask.

This is a fork of the [Flask-Cache](https://github.com/thadeusb/flask-cache)
extension and the following pull requests have been merged into this fork:

- [#90 Update documentation: route decorator before cache](https://github.com/thadeusb/flask-cache/pull/90)
- [#95 Pass the memoize parameters into unless().](https://github.com/thadeusb/flask-cache/pull/95)
- [#109 wrapped function called twice](https://github.com/thadeusb/flask-cache/pull/109)
- [#117 Moves setting the app attribute to the _set_cache method](https://github.com/thadeusb/flask-cache/pull/117)
- [#121 fix doc for delete_memoized](https://github.com/thadeusb/flask-cache/pull/121)
- [#122 Added proxy for werkzeug get_dict](https://github.com/thadeusb/flask-cache/pull/122)
- [#123 "forced_update" option to 'cache' and 'memoize' decorators](https://github.com/thadeusb/flask-cache/pull/123)
- [#124 Fix handling utf8 key args](https://github.com/thadeusb/flask-cache/pull/124) (cherry-picked)
- [#125 Fix unittest failing for redis unittest](https://github.com/thadeusb/flask-cache/pull/125)
- [#127 Improve doc for using @cached on view](https://github.com/thadeusb/flask-cache/pull/127)
- [#128 Doc for delete_memoized](https://github.com/thadeusb/flask-cache/pull/128)
- [#129 tries replacing inspect.getargspec with either signature or getfullargspec if possible](https://github.com/thadeusb/flask-cache/pull/129)

For the complete changelog, have a look at the ``CHANGES`` file.


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

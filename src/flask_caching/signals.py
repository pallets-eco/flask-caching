"""
flask_caching.signals
~~~~~~~~~~~~~~~~~~~~~

The signals for Flask-Caching.

:copyright: (c) 2026 by Peter Justin
:license: BSD, see LICENSE for more details.
"""

from blinker import Namespace

_signals = Namespace()

#: Sent when a view decorated with :meth:`~Cache.cached` is served from the
#: cache. It is passed ``cache``, the :class:`Cache` instance, ``cache_key``,
#: the key the response was found under, and ``args`` and ``kwargs``, the
#: arguments the view was called with.
cache_view_hit = _signals.signal("cache-view-hit")

#: Sent when a view decorated with :meth:`~Cache.cached` is not found in the
#: cache and has to be called. It is passed the same arguments as
#: :data:`cache_view_hit`.
cache_view_miss = _signals.signal("cache-view-miss")

#: Sent when a function decorated with :meth:`~Cache.memoize` is served from
#: the cache. In addition to the arguments passed to :data:`cache_view_hit`,
#: it is passed ``f``, the undecorated function.
cache_memoize_hit = _signals.signal("cache-memoize-hit")

#: Sent when a function decorated with :meth:`~Cache.memoize` is not found in
#: the cache and has to be called. It is passed the same arguments as
#: :data:`cache_memoize_hit`.
cache_memoize_miss = _signals.signal("cache-memoize-miss")

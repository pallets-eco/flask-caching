"""
flask_caching.backends.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the BaseCache that other caching
backends have to implement.

:copyright: (c) 2018 by Peter Justin.
:copyright: (c) 2010 by Thadeus Burgess.
:license: BSD, see LICENSE for more details.
"""

import warnings
from typing import Any
from typing import Self

from cachelib import BaseCache as CachelibBaseCache
from flask import Flask


class BaseCache(CachelibBaseCache):
    """Baseclass for the cache systems.  All the cache systems implement this
    API or a superset of it.

    .. deprecated:: 2.6.0
        Flask-Caching's backends will be removed in Flask-Caching 3.0.0.
        Use the cachelib backends instead, and subclass
        :class:`cachelib.BaseCache` for custom backends.

    :param default_timeout: The default timeout (in seconds) that is used if
                            no timeout is specified on ``set``. A timeout
                            of 0 indicates that the cache never expires.
    :param ignore_delete_many_errors: If set to ``False`` the ``delete_many``
                                      method raises a ``RuntimeError`` in case
                                      a key couldn't be deleted.
                                      Defaults to ``False``.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        # Warn from __new__ so every backend, including user subclasses, warns
        # exactly once per instance no matter how its __init__ chain looks.
        deprecated = next(
            klass
            for klass in cls.__mro__
            if klass.__module__.startswith("flask_caching.")
        )
        name = deprecated.__name__
        if deprecated is BaseCache:
            hint = "Subclass 'cachelib.BaseCache' instead."
        else:
            hint = (
                f"Use 'cachelib.{name}' instead: set CACHE_TYPE to"
                f" 'cachelib.{name}' and pass its arguments with CACHE_ARGS"
                " and CACHE_OPTIONS."
            )
        warnings.warn(
            f"'{deprecated.__module__}.{name}' is deprecated and will be removed"
            f" in Flask-Caching 3.0.0. {hint}",
            FutureWarning,
            stacklevel=2,
        )
        return super().__new__(cls)

    def __init__(
        self, default_timeout: int = 300, ignore_delete_many_errors: bool = False
    ) -> None:
        CachelibBaseCache.__init__(
            self,
            default_timeout=default_timeout,
            ignore_delete_many_errors=ignore_delete_many_errors,
        )

    @classmethod
    def factory(
        cls,
        app: Flask,
        config: dict[str, Any],
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> "BaseCache":
        return cls()

"""
flask_caching.backends.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the BaseCache that other caching
backends have to implement.

:copyright: (c) 2018 by Peter Justin.
:copyright: (c) 2010 by Thadeus Burgess.
:license: BSD, see LICENSE for more details.
"""

from typing import Any

from cachelib import BaseCache as CachelibBaseCache
from flask import Flask


class BaseCache(CachelibBaseCache):
    """Baseclass for the cache systems.  All the cache systems implement this
    API or a superset of it.

    :param default_timeout: The default timeout (in seconds) that is used if
                            no timeout is specified on ``set``. A timeout
                            of 0 indicates that the cache never expires.
    :param ignore_delete_many_errors: If set to ``False`` the ``delete_many``
                                      method raises a ``RuntimeError`` in case
                                      a key couldn't be deleted.
                                      Defaults to ``False``.
    """

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

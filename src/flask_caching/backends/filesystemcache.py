"""
flask_caching.backends.filesystem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The filesystem caching backend.

:copyright: (c) 2018 by Peter Justin.
:copyright: (c) 2010 by Thadeus Burgess.
:license: BSD, see LICENSE for more details.
"""

import hashlib
import logging
import warnings
from typing import Any

from cachelib import FileSystemCache as CachelibFileSystemCache
from flask import Flask

from flask_caching.backends.base import BaseCache

logger = logging.getLogger(__name__)


class FileSystemCache(BaseCache, CachelibFileSystemCache):
    """A cache that stores the items on the file system.  This cache depends
    on being the only user of the ``cache_dir``.  Make absolutely sure that
    nobody but this cache stores files there or otherwise the cache will
    randomly delete files therein.

    :param cache_dir: the directory where cache files are stored.
    :param threshold: the maximum number of items the cache stores before
                      it starts deleting some. A threshold value of 0
                      indicates no threshold.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    :param mode: the file mode wanted for the cache files, default 0600
    :param hash_method: Default :func:`~hashlib.sha256`. The hash method used to
                        generate the filename for cached results.
    :param ignore_delete_many_errors: If set to ``False`` the ``delete_many``
                                      method raises a ``RuntimeError`` in case
                                      a key couldn't be deleted.
                                      Defaults to ``False``.
    :param ignore_errors: Deprecated alias for ``ignore_delete_many_errors``.

        .. deprecated:: 2.5.0
           Will be removed in the next version.
    """

    def __init__(
        self,
        cache_dir: str,
        threshold: int = 500,
        default_timeout: int = 300,
        mode: int = 0o600,
        hash_method: Any = hashlib.sha256,
        ignore_delete_many_errors: bool = False,
        ignore_errors: bool | None = None,
    ) -> None:
        if ignore_errors is not None:
            warnings.warn(
                "'ignore_errors' is deprecated and will be removed in the next "
                "version. Use 'ignore_delete_many_errors' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            ignore_delete_many_errors = ignore_errors

        CachelibFileSystemCache.__init__(
            self,
            cache_dir=cache_dir,
            threshold=threshold,
            default_timeout=default_timeout,
            mode=mode,
            hash_method=hash_method,
            ignore_delete_many_errors=ignore_delete_many_errors,
        )

    @classmethod
    def factory(
        cls,
        app: Flask,
        config: dict[str, Any],
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> "FileSystemCache":
        args.insert(0, config["CACHE_DIR"])
        kwargs.update(
            dict(
                threshold=config["CACHE_THRESHOLD"],
                hash_method=config["CACHE_FILE_HASH_METHOD"],
            )
        )
        return cls(*args, **kwargs)

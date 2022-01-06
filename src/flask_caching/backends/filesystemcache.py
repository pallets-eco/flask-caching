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
import os
import pickle
from time import time

from cachelib import FileSystemCache as CachelibFileSystemCache

from flask_caching.backends.base import BaseCache

logger = logging.getLogger(__name__)


class FileSystemCache(BaseCache, CachelibFileSystemCache):

    """A cache that stores the items on the file system.  This cache depends
    on being the only user of the `cache_dir`.  Make absolutely sure that
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
    :param hash_method: Default hashlib.md5. The hash method used to
                        generate the filename for cached results.
    :param ignore_errors: If set to ``True`` the :meth:`~BaseCache.delete_many`
                          method will ignore any errors that occurred during the
                          deletion process. However, if it is set to ``False``
                          it will stop on the first error. Defaults to
                          ``False``.
    """

    def __init__(
        self,
        cache_dir,
        threshold=500,
        default_timeout=300,
        mode=0o600,
        hash_method=hashlib.md5,
        ignore_errors=False,
    ):

        BaseCache.__init__(self, default_timeout=default_timeout)
        CachelibFileSystemCache.__init__(
            self,
            cache_dir=cache_dir,
            threshold=threshold,
            default_timeout=default_timeout,
            mode=mode,
            hash_method=hash_method,
        )

        self.ignore_errors = ignore_errors

    @classmethod
    def factory(cls, app, config, args, kwargs):
        args.insert(0, config["CACHE_DIR"])
        kwargs.update(
            dict(
                threshold=config["CACHE_THRESHOLD"],
                ignore_errors=config["CACHE_IGNORE_ERRORS"],
            )
        )
        return cls(*args, **kwargs)

    def _list_dir(self):
        """return a list of (fully qualified) cache filenames"""
        mgmt_files = [
            self._get_filename(name).split("/")[-1] for name in (self._fs_count_file,)
        ]
        return [
            os.path.join(self._path, fn)
            for fn in os.listdir(self._path)
            if not fn.endswith(self._fs_transaction_suffix) and fn not in mgmt_files
        ]

    def _prune(self):
        if self._threshold == 0 or not self._file_count > self._threshold:
            return

        entries = self._list_dir()
        nremoved = 0
        now = time()
        for idx, fname in enumerate(entries):
            try:
                remove = False
                with open(fname, "rb") as f:
                    expires = pickle.load(f)
                remove = (expires != 0 and expires <= now) or idx % 3 == 0
                if remove:
                    os.remove(fname)
                    nremoved += 1
            except OSError:
                pass
        self._update_count(value=len(self._list_dir()))
        logger.debug("evicted %d key(s)", nremoved)

    def get(self, key):
        result = None
        expired = False
        hit_or_miss = "miss"
        filename = self._get_filename(key)
        try:
            with open(filename, "rb") as f:
                pickle_time = pickle.load(f)
                expired = pickle_time != 0 and pickle_time < time()
                if not expired:
                    hit_or_miss = "hit"
                    result = pickle.load(f)
            if expired:
                self.delete(key)
        except FileNotFoundError:
            pass
        except (OSError, pickle.PickleError) as exc:
            logger.error("get key %r -> %s", key, exc)
        expiredstr = "(expired)" if expired else ""
        logger.debug("get key %r -> %s %s", key, hit_or_miss, expiredstr)
        return result

    def has(self, key):
        result = False
        expired = False
        filename = self._get_filename(key)
        try:
            with open(filename, "rb") as f:
                pickle_time = pickle.load(f)
            expired = pickle_time != 0 and pickle_time < time()
            if expired:
                self.delete(key)
            else:
                result = True
        except FileNotFoundError:
            pass
        except (OSError, pickle.PickleError) as exc:
            logger.error("get key %r -> %s", key, exc)
        expiredstr = "(expired)" if expired else ""
        logger.debug("has key %r -> %s %s", key, result, expiredstr)
        return result

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
import tempfile
from time import time

from cachelib import FileSystemCache as CachelibFileSystemCache

from flask_caching.backends.base import BaseCache, extract_serializer_args

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
        **kwargs
    ):

        BaseCache.__init__(
            self,
            default_timeout=default_timeout,
            **extract_serializer_args(kwargs)
        )
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
                    expires, _ = self._serializer.load(f)
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
                data = self._serializer.load(f)
                if isinstance(data, int):
                    # backward compatibility
                    # should be removed in the next major release
                    pickle_time = data
                    result = self._serializer.load(f)
                else:
                    pickle_time, result = data
                expired = pickle_time != 0 and pickle_time < time()
            if expired:
                result = None
                self.delete(key)
            else:
                hit_or_miss = "hit"
        except FileNotFoundError:
            pass
        except Exception as exc:
            if exc is OSError or exc is self._serialization_error:
                logger.error("get key %r -> %s", key, exc)
            else:
                raise exc
        expiredstr = "(expired)" if expired else ""
        logger.debug("get key %r -> %s %s", key, hit_or_miss, expiredstr)
        return result

    def add(self, key, value, timeout=None):
        filename = self._get_filename(key)
        added = False
        should_add = not os.path.exists(filename)
        if should_add:
            added = self.set(key, value, timeout)
        addedstr = "added" if added else "not added"
        logger.debug("add key %r -> %s", key, addedstr)
        return should_add

    def set(self, key, value, timeout=None, mgmt_element=False):
        result = False

        # Management elements have no timeout
        if mgmt_element:
            timeout = 0

        # Don't prune on management element update, to avoid loop
        else:
            self._prune()

        timeout = self._normalize_timeout(timeout)
        filename = self._get_filename(key)
        try:
            fd, tmp = tempfile.mkstemp(
                suffix=self._fs_transaction_suffix, dir=self._path
            )
            with os.fdopen(fd, "wb") as f:
                self._serializer.dump((timeout, value), f)

            # https://github.com/sh4nks/flask-caching/issues/238#issuecomment-801897606
            is_new_file = not os.path.exists(filename)
            if not is_new_file:
                os.remove(filename)
            os.replace(tmp, filename)

            os.chmod(filename, self._mode)
        except OSError as exc:
            logger.error("set key %r -> %s", key, exc)
        else:
            result = True
            logger.debug("set key %r", key)
            # Management elements should not count towards threshold
            if not mgmt_element and is_new_file:
                self._update_count(delta=1)
        return result

    def delete(self, key, mgmt_element=False):
        deleted = False
        try:
            os.remove(self._get_filename(key))
        except FileNotFoundError:
            logger.debug("delete key %r -> no such key")
        except (OSError) as exc:
            logger.error("delete key %r -> %s", key, exc)
        else:
            deleted = True
            logger.debug("deleted key %r", key)
            # Management elements should not count towards threshold
            if not mgmt_element:
                self._update_count(delta=-1)
        return deleted

    def has(self, key):
        result = False
        expired = False
        filename = self._get_filename(key)
        try:
            with open(filename, "rb") as f:
                pickle_time, _ = self._serializer.load(f)
            expired = pickle_time != 0 and pickle_time < time()
            if expired:
                self.delete(key)
            else:
                result = True
        except FileNotFoundError:
            pass
        except Exception as exc:
            if exc is OSError or exc is self._serialization_error:
                logger.error("get key %r -> %s", key, exc)
            else:
                raise exc
        expiredstr = "(expired)" if expired else ""
        logger.debug("has key %r -> %s %s", key, result, expiredstr)
        return result

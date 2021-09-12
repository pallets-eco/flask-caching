"""
    flask_caching.backends.filesystem
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The filesystem caching backend.

    :copyright: (c) 2018 by Peter Justin.
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
import errno
import hashlib
import logging
import os
import tempfile
from time import time

from flask_caching.backends.base import BaseCache

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle  # type: ignore


logger = logging.getLogger(__name__)


class FileSystemCache(BaseCache):

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

    #: used for temporary files by the FileSystemCache
    _fs_transaction_suffix = ".__wz_cache"
    #: keep amount of files in a cache element
    _fs_count_file = "__wz_cache_count"

    def __init__(
        self,
        cache_dir,
        threshold=500,
        default_timeout=300,
        mode=0o600,
        hash_method=hashlib.md5,
        ignore_errors=False,
    ):
        super().__init__(default_timeout)
        self._path = cache_dir
        self._threshold = threshold
        self._mode = mode
        self._hash_method = hash_method
        self.ignore_errors = ignore_errors

        try:
            os.makedirs(self._path)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

        # If there are many files and a zero threshold,
        # the list_dir can slow initialisation massively
        if self._threshold != 0:
            self._update_count(value=len(self._list_dir()))

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

    @property
    def _file_count(self):
        return self.get(self._fs_count_file) or 0

    def _update_count(self, delta=None, value=None):
        # If we have no threshold, don't count files
        if self._threshold == 0:
            return

        if delta:
            new_count = self._file_count + delta
        else:
            new_count = value or 0
        self.set(self._fs_count_file, new_count, mgmt_element=True)

    def _normalize_timeout(self, timeout):
        timeout = BaseCache._normalize_timeout(self, timeout)
        if timeout != 0:
            timeout = time() + timeout
        return int(timeout)

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

    def clear(self):
        for fname in self._list_dir():
            try:
                os.remove(fname)
            except OSError:
                self._update_count(value=len(self._list_dir()))
                return False
        self._update_count(value=0)
        return True

    def _get_filename(self, key):
        if isinstance(key, str):
            key = key.encode("utf-8")  # XXX unicode review
        hash = self._hash_method(key).hexdigest()
        return os.path.join(self._path, hash)

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
                pickle.dump(timeout, f, 1)
                pickle.dump(value, f, pickle.HIGHEST_PROTOCOL)

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

import json as _json
try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle  # type: ignore


class BytesSerializer:
    """Serializer wrapper with auto str2bytes casting"""
    def __init__(self, serializer):
        self._serializer = serializer

    def dumps(self, obj, *args, **kwargs):
        result = self._serializer.dumps(obj, *args, **kwargs)
        if isinstance(result, str):
            return result.encode()
        return result

    def dump(self, obj, fp, *args, **kwargs):
        fp.write(self.dumps(obj, *args, **kwargs))

    def loads(self, obj, *args, **kwargs):
        if isinstance(obj, bytes):
            obj = obj.decode()
        return self._serializer.loads(obj, *args, **kwargs)

    def load(self, fp, *args, **kwargs):
        return self.loads(fp.read(), *args, **kwargs)


json = BytesSerializer(_json)
JSONError = _json.JSONDecodeError

PickleError = pickle.PickleError

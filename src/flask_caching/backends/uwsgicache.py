import warnings
from typing import Any

from flask_caching.contrib.uwsgicache import UWSGICache as _UWSGICache


class UWSGICache(_UWSGICache):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "Importing UWSGICache from flask_caching.backends is deprecated, "
            "use flask_caching.contrib.uwsgicache.UWSGICache instead. "
            "This will be removed in a future version.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        super().__init__(*args, **kwargs)

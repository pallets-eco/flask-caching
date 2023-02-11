"""
    flask_caching.backends.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the BaseFactory that other caching
    backends have to implement.

    :copyright: (c) 2018 by Peter Justin.
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""


class BaseFactory:
    """Baseclass for the cache systems. All the cache systems implement this
    API or a superset of it.
    """

    @classmethod
    def factory(cls, app, config, args, kwargs):
        return cls()

from __future__ import absolute_import, division, print_function


__version__ = '0.15.0.dev0'

try:
    from glue._githash import __githash__, __dev_value__  # noqa
    __version__ += __dev_value__
except Exception:
    pass

from __future__ import absolute_import

__version__ = '5.8.1'

from .compiler import Compiler  # noqa
from .ext import html
from .filters import register_filter  # noqa
from .parser import Parser  # noqa
from .utils import process  # noqa


def simple_convert(template):
    return html.process_pugjs(template)

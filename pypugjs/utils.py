import six
from collections import OrderedDict as odict
from copy import deepcopy

from .compiler import Compiler
from .ext.html import Compiler as HTMLCompiler
from .parser import Parser


missing = object()
izip, imap = zip, map


def process(src,filename=None, parser=Parser, compiler=HTMLCompiler, **kwargs):
    _parser = parser(src, filename=filename)
    block = _parser.parse()
    _compiler = compiler(block, **kwargs)
    return _compiler.compile().strip()

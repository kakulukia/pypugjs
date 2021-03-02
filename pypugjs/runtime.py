from __future__ import absolute_import

from itertools import chain

import six
from six.moves import reduce

from chardet.universaldetector import UniversalDetector
import io

try:
    from collections.abc import Mapping as MappingType
except ImportError:
    import UserDict

    MappingType = (UserDict.UserDict, UserDict.DictMixin, dict)


def escape(s):
    """Convert the characters &, <, >, ' and " in string s to HTML-safe
    sequences.  Use this if you need to display text that might contain
    such characters in HTML.  Marks return value as markup string.
    """
    if hasattr(s, '__html__'):
        return s.__html__()
    if isinstance(s, six.binary_type):
        s = six.text_type(str(s), 'utf8')
    elif isinstance(s, six.text_type):
        s = s
    else:
        s = str(s)

    return (
        s.replace('&', '&amp;')
        .replace('>', '&gt;')
        .replace('<', '&lt;')
        .replace("'", '&#39;')
        .replace('"', '&#34;')
    )


def attrs(attrs=None, terse=False, undefined=None):
    if attrs is None:
        attrs = []

    def extract_classes(cls):
        """Recursively extract_class from iterable and mappings"""
        if isinstance(cls, (list, tuple)):
            return tuple(reduce(lambda t1, t2: t1 + t2, map(extract_classes, cls)))
        if isinstance(cls, dict):
            return tuple(
                sorted(dict(filter(lambda x: x[1] and x[1] != undefined, cls.items())))
            )
        return (str(cls),)

    buf = []
    if bool(attrs):
        buf.append(u'')
        for k, v in attrs:
            if undefined is not None and isinstance(v, undefined):
                continue
            if v is not None and (v or type(v) != bool):
                if k == 'class':
                    v = u' '.join(extract_classes(v))
                t = v and type(v) == bool
                if t and not terse:
                    v = k
                buf.append(u'%s' % k if terse and t else u'%s="%s"' % (k, escape(v)))
    return u' '.join(buf)


def is_mapping(value):
    return isinstance(value, MappingType)


def is_iterable(ob):
    if isinstance(ob, six.string_types):
        return False
    try:
        iter(ob)
        return True
    except TypeError:
        return False


def get_cardinality(ob):
    if isinstance(ob, six.string_types):
        return 1
    try:
        return len(ob)
    except TypeError:
        return 1


def iteration(obj, num_keys):
    """
    PugJS iteration supports "for 'value' [, key]?" iteration only.
    PyPugJS has implicitly supported value unpacking instead, without
    the list indexes. Trying to not break existing code, the following
    rules are applied:

      1. If the object is a mapping type, return it as-is, and assume
         the caller has the correct set of keys defined.

      2. If the object's values are iterable (and not string-like):
         a. If the number of keys matches the cardinality of the object's
            values, return the object as-is.
         b. If the number of keys is one more than the cardinality of
            values, return a list of [v(0), v(1), ... v(n), index]

      3. Else the object's values are not iterable, or are string like:
         a. if there's only one key, return the list
         b. otherwise return a list of (value,index) tuples

    """

    # If the object is a mapping type, return it as-is
    if is_mapping(obj):
        return obj

    _marker = []

    iter_obj = iter(obj)
    head = next(iter_obj, _marker)
    iter_obj = chain([head], iter_obj)

    if head is _marker:
        # Empty list
        return []

    if is_iterable(head):
        cardinality = get_cardinality(head)
        if cardinality > 0 and num_keys == cardinality + 1:
            return (tuple(item) + (ix,) for ix, item in enumerate(iter_obj))
        else:
            return iter_obj

    elif num_keys == 2:
        return ((item, ix) for ix, item in enumerate(iter_obj))

    else:
        return iter_obj


def open(
    file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True
):
    rawdata = io.open(file, mode='rb')

    detector = UniversalDetector()
    for line in rawdata.readlines():
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    rawdata.close()

    decoded = io.open(
        file,
        mode=mode,
        buffering=buffering,
        encoding=detector.result["encoding"],
        errors=errors,
        newline=newline,
        closefd=closefd,
    )

    return decoded

"""
findfile and finddir --- unix find style util
(C) 2010 Ji Han (jihan917<at>yahoo<dot>com).
"""

import os


def flatten(I):
    if isinstance(I, basestring): return [I]
    ret = []
    try:
        for it in I: ret.extend(flatten(it))
    except TypeError:
        ret.extend([I])
    finally:
        return ret


def findfile(pathname, *visitors):
    """
    search for files in a directory hierarchy.
    visitors should accept a pathname and return a bool.
    on finishing a visit, files yielding true will continue to next round.
    e.g. to remove all pyc files from Python's Lib directory:
    find.findfile(r'c:\python27\lib', lambda _: _.endswith('.pyc'), os.remove)
    """
    reduce(lambda a, b: filter(b, a),
           visitors,
           flatten(map(lambda s: map(lambda t: os.path.join(s[0], t), s[2]),
                       os.walk(pathname))))


def finddir(pathname, *visitors):
    "search for directories in a directory hierarchy."
    reduce(lambda a, b: filter(b, a),
           visitors,
           flatten(map(lambda s: map(lambda t: os.path.join(s[0], t), s[1]),
                       os.walk(pathname))))


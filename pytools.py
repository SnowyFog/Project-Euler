import collections
import itertools


class NotGivenType:
    """For instantiating an object NotGiven denoting that no value was given.

    NotGiven can be used as a default argument to a function that needs to
    differentiate between a case where no value was given from every other
    case.  Use (x is NotGiven) to determine whether a value was given.

    NotGiven is considered false.

    There should be only one instance of this type."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __bool__(self):
        return False

    def __repr__(self):
        return 'NotGiven'

# The name 'NotGiven' is written in capitalized words in accordance with the
# name of the built-in value None.
NotGiven = NotGivenType()

def isgiven(x):
    return x is not NotGiven

def if_given(*args, **kwargs):
    """Return all arguments that are except for those that are NotGiven.

    Take either either positional or keyword arguments.  Return a sequence for
    positional arguments or a mapping for keyword arguments.

    >>> range(*if_given(8, NotGiven, NotGiven))
    range(0, 8)
    >>> int(**if_given(x='10', base=NotGiven))
    10
    """

    if args and kwargs:
        raise TypeError("use either positional or keyword arguments, not both")

    if args:
        args_iter = iter(args)
        given_args = tuple(itertools.takewhile(isgiven, args_iter))
        if any(isgiven(x) for x in args_iter):
            raise ValueError("no argument with a proper value should come "
                             "after NotGiven")
        return given_args

    # The default is a mapping because it allows unpacking empty sequences or
    # mappings to if_given.  That is, f(*if_given(*())) and f(**if_given(**{}))
    # both work.
    return {k: v for k, v in kwargs.items() if isgiven(v)}


def group(iterable, key=None):
    """Return a dictionary mapping each key to a list of values.

    <key> is a function used to generate the keys which the items of <iterable>
    are grouped by.  If <key> is not specified or None, <iterable> must consist
    of key-value pairs, where the keys are used to group the values.

    >>> group(['ham', 'or', 'tea'], key=len) == {2: ['or'], 3: ['ham', 'tea']}
    >>> group([('a', 1), ('a', 7), ('b', 0)]) == {'a': [1, 7], 'b': [0]} """

    groups = collections.defaultdict(list)
    if key is None:
        for k, v in iterable:
            groups[k].append(v)
    else:
        for x in iterable:
            groups[key(x)].append(x)
    return groups


# Inherit from Counter first because the __init__() and update() methods should
# come from Counter.
class OrderedCounter(collections.Counter, collections.OrderedDict):
    """Counter that remembers the order items are first encountered in."""

    def __repr__(self):
        format_str = '{type_name}({reduction!r})' if self else '{type_name}()'
        return format_str.format(type=type(self).__name__,
                                 reduction=self._reduction())

    def __reduce__(self):
        return type(self), (self._reduction(),)

    def _reduction(self):
        return collections.OrderedDict(self)


def defaults_tuple(type_name, defaults):
    """Return a function that returns named tuples with default values.

    Note:  Different instances of the named tuple will share items that were
    given as default values.  Use immutable types if the items should not be
    modified."""

    DefaultsTuple = collections.namedtuple(type_name, defaults)
    return DefaultsTuple(**defaults)._replace


forever = itertools.repeat(None)

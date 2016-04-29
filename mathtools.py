import collections
import fractions
import functools
import itertools
import math
import operator

import checkinput
from pytools import NotGiven, if_given, isgiven


ERROR_MSGS = dict(
  INDEX_OUT_OF_RANGE = "index out of range"
)


def product(iterable):
    return functools.reduce(operator.imul, iterable, 1)


def counter_union(iterable):
    return functools.reduce(operator.ior, iterable, collections.Counter())


def arithmetic_series(a, b=NotGiven, step=NotGiven):
    """Return the sum of all integers in the specified range.
    
    The specified range is equivalent to the range recieved from a call to 
    range() with the same arguments.
    
    >>> arithmetic_series(8) == sum(range(8))
    True
    >>> arithmetic_series(-4, 10, 3) == sum(range(-4, 10, 3))
    True
    """
    
    seq = range(*if_given(a, b, step))
    
    if __debug__:
        if seq.start > seq.stop:
            raise ValueError("the start of the range must not be greater than "
                             "the end")
        checkinput.must_be_positive_int(seq.step)

    # We can't use (not seq) to determine whether <seq> is empty because this
    # fails if the length of the range is too large to fit into a C long.
    if seq.start == seq.stop:
        return 0
    
    # For the same reason, we can't use len(seq) to determine the number of
    # elements.
    first = seq[0]
    last = seq[-1]
    num_elements = (last - first) // seq.step + 1
    
    # The average element of the sequence is equal to the average of the first
    # and the last element.
    return num_elements * (first + last) // 2


def item_by_index(iterable, index):
    """Return the item of <iterable> with the given index.
    
    Can be used even if <iterable> does not support indexing.  <index> can be
    any integer.  The indexing rules are the same as with built-in indexable
    types.
    
    Raise an IndexError if <iterable> does not yield enough items."""
    
    if __debug__:
        checkinput.must_be_int(index)
    
    if index < 0:
        return _item_by_negative_index(iterable, index)
    
    iterable_slice = itertools.islice(iterable, index, None)
    try:
        return next(iterable_slice)
    except StopIteration:
        raise IndexError(ERROR_MSGS["INDEX_OUT_OF_RANGE"]) from None

def _item_by_negative_index(iterable, index):
    num_items_to_be_saved = -index
    tail = collections.deque(iterable, maxlen=num_items_to_be_saved)
    try:
        return tail[index]
    except IndexError:
        raise IndexError(ERROR_MSGS["INDEX_OUT_OF_RANGE"]) from None


def items_before(iterable, limit):
    """Yield the items of <iterable> while they are less than <limit>."""
    return itertools.takewhile(lambda x: x < limit, iterable)


def primes():
    """Generate the prime numbers."""
    yield 2
    for n in _possible_odd_primes():
        if all(n % d != 0 for d in _odd_divisor_candidates(n)):
            yield n

def prime_factors(n):
    """Generate the prime factors of <n> in ascending order."""
    
    if __debug__:
        checkinput.must_be_positive_int(n)
    
    if n == 1:
        return
    
    # Extract prime factors from <n>, dividing <n> by each factor when the
    # factor is found.
    possible_odd_factors = iter(_possible_odd_primes())
    divisor = 2
    next_factor_limit = _least_divisor_limit(n)
    while divisor < next_factor_limit:
        if n % divisor == 0:
            yield divisor
            n //= divisor
            next_factor_stop = _least_divisor_limit(n)
        else:
            divisor = next(possible_odd_factors)
    yield n

def prime_factor_counter(n):
    """Return the prime factors of <n> in a counter."""
    return collections.Counter(prime_factors(n))

def _possible_odd_primes():
    return itertools.count(3, 2)

def _odd_divisor_candidates(n):
    """Return an iterable of possible least odd non-trivial divisors of <n>."""
    return range(3, _least_divisor_limit(n), 2)

def _least_divisor_limit(n):
    """Return an exclusive upper limit for the least non-trivial divisor."""
    return int(math.sqrt(n)) + 1


binary_gcd = fractions.gcd

def binary_lcm(a, b):
    """Return the least common multiple of <a> and <b>."""
    return a // binary_gcd(a, b) * b

def gcd(numbers):
    """Return the greatest common divisor of <numbers>."""
    return functools.reduce(binary_gcd, numbers)

def lcm(numbers):
    """Return the least common multiple of <numbers>."""
    return functools.reduce(binary_lcm, numbers)


def fibonacci_numbers():
    """Generate the fibonacci sequence."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a+b


def is_decimal_palindrome(n):
    """Return True if <n> is a palindrome in base ten."""
    
    if __debug__:
        checkinput.must_be_natural_number(n)
    
    n_str = str(n)
    return n_str == n_str[::-1]

import numbers


def must_be_non_negative(x):
    if x < 0:
        raise ValueError("a non-negative number is required")

def must_be_positive(x):
    if x <= 0:
        raise ValueError("a positive number is required")


def must_be_int(x):
    if not isinstance(x, numbers.Integral):
        raise TypeError("an integer is required")

def must_be_natural_number(x):
    must_be_int(x)
    must_be_non_negative(x)

def must_be_positive_int(x):
    must_be_int(x)
    must_be_positive(x)

import abc
import collections.abc
import itertools
import numbers


class AbstractType(metaclass=abc.ABCMeta):
    """"""
    
    @abc.abstractmethod
    def has_instance(self, x):
        """Return True if <x> is an instance of this abstract type."""
        return True
    
    @abc.abstractmethod
    def edge_cases(self):
        """Generate the edge cases for this abstract type."""


class _Int(AbstractType):
    """"""
    
    def has_instance(self, x):
        return isinstance(x, numbers.Integral) and super().has_instance(x)
    
    def edge_cases(self):
        yield from ()

    def __repr__(self):
        return 'int'

int_ = _Int()
    

class _IntAtLeast(_Int):
    """"""
    
    def __init__(self, min_, name, **kwargs):
        super().__init__(**kwargs)
        self._min = min_
        self._name = name
    
    def has_instance(self, x):
        return x >= self._min and super().has_instance(x)
    
    def edge_cases(self):
        yield self._min

    def __repr__(self):
        return self._name

natural_number = _IntAtLeast(0, "natural_number")
positive_int = _IntAtLeast(1, "positive_int")


class CollectionOf(AbstractType):
    """must be iterable"""
    
    def __init__(self, element_type, **kwargs):
        if not isinstance(element_type, AbstractType):
            raise TypeError("the element type must be an AbstractType")
        
        super().__init__(**kwargs)
        self._element_type = element_type
    
    def has_instance(self, x):
        return (isinstance(x, collections.abc.Container) and
                all(self._element_type.has_instance(element)
                    for element in x) and
                super().has_instance(x))
    
    def __repr__(self):
        return '{type_name}({element_type!r})'.format(
                   type_name=type(self).__name__,
                   element_type=self._element_type)

class ListOf(CollectionOf):
    """"""
    
    def has_instance(self, x):
        return (isinstance(x, collections.abc.List) and
                super().has_instance(x))
    
    def edge_cases(self):
        element_edge_cases = tuple(self._element_type.edge_cases())
        for n in range(len(element_edge_cases) + 1):
            yield from itertools.permutations(element_edge_cases, n)

class SetOf(CollectionOf):
    """"""
    
    def has_instance(self, x):
        return (isinstance(x, collections.abc.Set) and
                super().has_instance(x))
    
    def edge_cases(self):
        element_edge_cases = list(self._element_type.edge_cases())
        for n in range(len(element_edge_cases) + 1):
            for combination in itertools.combinations(element_edge_cases, n):
                yield frozenset(combination)

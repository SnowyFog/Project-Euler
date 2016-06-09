import importlib
import numbers

import pytools


LAST_PROBLEM_ID = 8

# Must be small enough that a column of solvers isn't too wide in the output,
# and large enough to allow descriptive solver names.
SOLVER_NAME_MAX_LEN = 26

_PROBLEM_ID_NUM_DIGITS = 3


class WrongProblemError(Exception):
    """A problem module contains a problem with the wrong ID."""


class Problem:
    """Project Euler problem with parameters, solution and solvers."""

    def __init__(self, problem_id, actual_args_dict, *, solution=None,
                 domain=None, test_dicts=()):
        self.problem_id = problem_id
        self.get_args = pytools.defaults_tuple('ProblemArgs', actual_args_dict)
        self.actual_args = self.get_args()
        self.solution = solution
        self.domain = domain
        self.tests = [self.get_args(**test_dict) for test_dict in test_dicts]

        self.solvers = []

    def list_as_solver(self, solver):
        """Decorator to append the decorated function to the list of solvers.

        The length of the decorated function's name must be no more than
        SOLVER_NAME_MAX_LEN."""

        assert len(solver.__name__) <= SOLVER_NAME_MAX_LEN
        self.solvers.append(solver)
        return solver

    @staticmethod
    def is_valid_result(result):
        """Return whether the given result is of a valid type.

        The value None can't be a valid result because it would compare equal
        to `self.solution` if the correct solution is not known."""

        return isinstance(result, numbers.Integral)


def get_problem(problem_id):
    relative_module_name = _get_relative_name(problem_id)
    try:
        module = importlib.import_module(relative_module_name, __name__)
    except ImportError:
        raise
    except Exception:
        raise ImportError()

    if module.problem.problem_id != problem_id:
        raise WrongProblemError()

    return module.problem

def _get_relative_name(problem_id):
    return '.p' + str(problem_id).zfill(_PROBLEM_ID_NUM_DIGITS)

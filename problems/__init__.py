"""Package containing Project Euler problems.

Problem objects are located in modules in this package and should not be
accessed directly, but rather through the function get_problem() defined in
this package."""


import collections
import importlib
import numbers


LAST_PROBLEM_ID = 8

# SOLVER_NAME_MAX_LEN must be small enough that a column of solvers isn't too
# wide in the output, and large enough to allow descriptive solver names.
SOLVER_NAME_MAX_LEN = 26

_PROBLEM_ID_NUM_DIGITS = 3


class WrongProblemError(Exception):
    """A problem module contains a problem with the wrong ID."""


class ProblemImportError(Exception):
    """A problem object could not be imported from its module."""


class Problem:
    """Project Euler problem with arguments, solution and solvers.

    This is a generalized version of a Project Euler problem where the input
    parameters can vary.

    == Instance attributes ==

    actual_args
        A named tuple containing the arguments of the problem as given by
        Project Euler.
    domain
        The domain of definition of the problem viewed as a mathematical
        function.  Arguments to solvers must belong to this domain.  A value of
        None means that the domain is not available.
    get_args(**args)
        A function that takes, as positional arguments, arguments for the
        problem and returns a named tuple containing them.  If a parameter is
        not defined, its value from `actual_args` is used.
    problem_id
        The problem's ID, as given by Project Euler.
    solution
        The problem's solution, as verified by Project Euler.  A value of None
        means that the solution is not available.
    solvers
        An iterable of functions that solve a generalized version of this
        problem.  Each solver takes the problem's arguments in the form of a
        named tuple like `actual_args` or the ones returned by get_args()."""

    def __init__(self, problem_id, actual_args_dict, *, domain=None,
                 solution=None):
        self.problem_id = problem_id
        self.domain = domain
        self.solution = solution
        self.solvers = []

        Args = collections.namedtuple('ProblemArgs', actual_args_dict)
        self.actual_args = Args(**actual_args_dict)
        self.get_args = self.actual_args._replace

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
        to `problem.solution` if the correct solution is not known."""

        return isinstance(result, numbers.Integral)


def get_problem(problem_id):
    """Import a problem module and return the problem object from it."""

    module_name = _get_module_name(problem_id)
    try:
        problem = importlib.import_module(module_name).problem
    except Exception as e:
        raise ProblemImportError("could not import problem object") from e

    if problem.problem_id != problem_id:
        raise WrongProblemError("problem module contains wrong problem")

    return problem

def _get_module_name(problem_id):
    return 'problems.p' + str(problem_id).zfill(_PROBLEM_ID_NUM_DIGITS)

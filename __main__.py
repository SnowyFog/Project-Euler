"""Command-line script for examining solvers for Project Euler problems.

This script performs certain predefined actions on solvers for problems in the
`problems` package.  It can
  - use the solvers to attempt to solve the problem they belong to,
  - list the available solvers,
  - (TODO) test the solvers' correctness, and
  - (TODO) measure the solvers' performance.
Results are printed to stdout.

An "action", within the context of this script, is a function that takes a
problem and a list of solvers, performs some operations on them and prints
results to stdout.  A "solver" is a function that solves a Project Euler
problem."""


import argparse
import collections
import types

import problems
import timingtools


MAX_EXECUTIONS = 100
RESULT_TIMEOUT = 10
TARGET_TIME = 1
TIMING_MS_DECIMALS = 3
TIMING_TIMEOUT = 4

# OUTCOME_STR_MAX_LEN must be small enough that a column of outcomes isn't too
# wide in the terminal, and large enough that normal results can be displayed.
OUTCOME_STRS = types.SimpleNamespace(
    CORRECT="correct",
    INVALID_RESULT_TYPE="type error",
    MEMORY_ERROR="memory error",
    OTHER_ERROR="unknown error",
    RECURSION_ERROR="recursion error",
    TIMEOUT="timeout",
    TOO_LONG_TO_PRINT="number too long",
)
OUTCOME_STR_MAX_LEN = max(len(s) for s in vars(OUTCOME_STRS).values())


def print_action(problem_id, action, solver_strs=None):
    """Print the output of an action performed on a problem.

    Get the problem with ID `problem_id` and perform `action` on it, using the
    solvers whose names match `solver_strs` and printing results to stdout.  If
    `solver_strs` is None, all of the problem's solvers are used."""

    print("== Problem {} ==".format(problem_id))

    try:
        problem = problems.get_problem(problem_id)
    except problems.ProblemImportError:
        print("Import failed.")
    except problems.WrongProblemError:
        print("The module for problem {} contains a wrong problem."
              .format(problem_id))
    else:
        solvers, unmatched_strs = find_solvers(problem, solver_strs)
        for unmatched_str in unmatched_strs:
            print("There is no solver starting with {!r}."
                  .format(unmatched_str))
        if solvers:
            action(problem, solvers)

    print()


def find_solvers(problem, solver_strs=None):
    """Find solvers that match the given search strings.

    Return a tuple of matching solvers of `problem` and unmatched search
    strings.  A solver matches a string if the solver's name starts with the
    string.  The matching solvers are returned in the order in which they were
    first matched.

    If `solver_strs` is None, all of the problem's solvers are returned."""

    if solver_strs is None:
        return problem.solvers.copy(), []

    matching_solvers = collections.OrderedDict()  # used as an ordered set
    unmatched_strs = []
    for solver_str in solver_strs:
        matches = [solver for solver in problem.solvers
                   if solver.__name__.startswith(solver_str)]
        for match in matches:
            matching_solvers[match] = None
        if not matches:
            unmatched_strs.append(solver_str)

    return matching_solvers, unmatched_strs


def print_solutions(problem, solvers):
    """Solve a problem with an iterable of solvers and print the outcomes."""
    if problem.solution is not None:
        print("Solution:", problem.solution)
    for solver in solvers:
        print_outcome_line(solver, get_solving_outcome_str(problem, solver))

def get_solving_outcome_str(problem, solver):
    """Solve a problem with a solver and return an outcome string.

    Try to solve `problem` with `solver`, using the problem's actual arguments.
    Return a string indicating the outcome of the attempt."""

    try:
        result = solver(problem.actual_args)
    except MemoryError:
        return OUTCOME_STRS.MEMORY_ERROR
    except RecursionError:
        return OUTCOME_STRS.RECURSION_ERROR
    except Exception:
        return OUTCOME_STRS.OTHER_ERROR

    if not problem.is_valid_result(result):
        return OUTCOME_STRS.INVALID_RESULT_TYPE
    if result == problem.solution:
        return OUTCOME_STRS.CORRECT
    if len(str(result)) > OUTCOME_STR_MAX_LEN:
        return OUTCOME_STRS.TOO_LONG_TO_PRINT
    return str(result)


def print_solvers(problem, solvers):
    """Print the given solvers.

    The parameter `problem` exists so that `print_solvers` can be used as an
    action."""

    for solver in solvers:
        print(solver.__name__)


def print_correctness_tests(problem, solvers):
    """Test the correctness of the given solvers and print the outcomes."""


def print_performances(problem, solvers):
    """Test the performance of the given solvers and print the outcomes."""

    timers = [timingtools.SingleArgTimer(solver) for solver in solvers]

    for test_index, test in enumerate(problem.performance_tests):
        print("Performance test {}".format(test_index))
        new_timers = []
        for timer in timers:
            try:
                timing = timer.min_run_time(test, TARGET_TIME, TIMING_TIMEOUT,
                                            MAX_EXECUTIONS)
            except timingtools.Timeout:
                timing_str = OUTCOME_STRS.TIMEOUT
            except MemoryError:
                timing_str = OUTCOME_STRS.MEMORY_ERROR
            except timingtools.CalleeError:
                timing_str = OUTCOME_STRS.FAILED
            else:
                format_values = dict(time=timing*1000,
                                     decimals=TIMING_MS_DECIMALS)
                timing_str = "{time:.{decimals}f}ms".format(**format_values)
                new_timers.append(timer)
            print_outcome_line(timer.func, timing_str)
        timers = new_timers


def print_outcome_line(solver, outcome_str):
    """Print a line indicating the outcome of an operation on a solver."""
    print("{solver:.<{solver_width}}..{outcome:.>{outcome_width}}"
          .format(solver=solver.__name__,
                  solver_width=problems.SOLVER_NAME_MAX_LEN,
                  outcome=outcome_str, outcome_width=OUTCOME_STR_MAX_LEN))


def parse_args():
    """Parse command-line arguments and return them in a namespace.

    The returned namespace has the following attributes:
      - `action`, the requested action.
      - `problem_id`, the ID of the requested problem.  A value of None means
        that all problems should be examined.
      - `solver_strs`, a list of strings indicating which solvers should be
        used.  A value of None means that all solvers should be used.

    If the arguments are invalid, print a usage message to stderr and exit."""

    actions_by_name = collections.OrderedDict([
        ('solve', print_solutions),
        ('list', print_solvers),
        ('test', print_correctness_tests),
        ('time', print_performances),
    ])
    default_action_name = 'solve'

    parser = argparse.ArgumentParser(
        description="Examine solver functions for Project Euler problems.")

    parser.add_argument(
        'action', nargs='?', choices=actions_by_name,
        default=default_action_name,
        help="desired action (default: {})".format(default_action_name))
    parser.add_argument(
        'problem_id', nargs='?', type=int, metavar='problem',
        help="ID of the problem to be examined (default: all problems)")
    parser.add_argument(
        'solver_strs', nargs='*', metavar='solver',
        help="desired solver function (default: all solvers)")

    args = parser.parse_args()
    args.action = actions_by_name[args.action]
    if not args.solver_strs:
        args.solver_strs = None
    return args


def main():
    """Let the user examine solvers via command-line arguments."""

    args = parse_args()

    if args.problem_id is None:
        problem_ids = range(1, problems.LAST_PROBLEM_ID+1)
    else:
        if not 1 <= args.problem_id <= problems.LAST_PROBLEM_ID:
            raise SystemExit("error: problem ID must be between 1 and {}"
                             .format(problems.LAST_PROBLEM_ID))
        problem_ids = [args.problem_id]

    for problem_id in problem_ids:
        print_action(problem_id, args.action, args.solver_strs)

main()

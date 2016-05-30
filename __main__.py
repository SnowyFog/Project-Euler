import argparse
import collections
import numbers
import sys

import problems
import timingtools


LAST_PROBLEM_ID = 8

VALID_RESULT_TYPES = (
    numbers.Integral,
)

RESULT_TIMEOUT = 10

TARGET_TIME = 1
TIMING_TIMEOUT = 4
MAX_EXECUTIONS = 100

TIMING_MS_DECIMALS = 3

SOLVER_NAME_MAX_LEN = 26
OUTCOME_STR_MAX_LEN = 15

OUTCOME_STRS = dict(
    CORRECT="correct",
    FAILED="failed",
    TIMEOUT="timeout",
    MEMORY_ERROR="memory error",
)


def print_action(problem_id, action, solver_strs=None):
    """Print the output of an action performed on a problem.

    Import the problem with ID <problem_id> and perform <action> on it, using
    the solvers whose names match <solver_strs>.  Print feedback to the user.

    If <solver_strs> is None, all of the problem's solvers are used."""

    try:
        problem = problems.get_problem(problem_id)
    except ImportError:
        print("Import of problem {} failed.".format(problem_id))
    except problems.WrongProblemError:
        print("The module for problem {} contains a wrong problem."
              .format(problem_id))
    else:
        print("# Problem", problem_id)
        solvers, unmatched_strs = find_solvers(problem, solver_strs)
        for unmatched_str in unmatched_strs:
            print("There is no solver starting with {!r}."
                  .format(unmatched_str))
        action(problem, solvers)

    print()


def find_solvers(problem, solver_strs=None):
    """Find solvers that match the given search strings.

    Return a tuple of matching solvers and unmatched search strings.  A solver
    matches a string if the solver's name starts with the string.  The matching
    solvers are returned in the order in which they were first matched.

    If <solver_strs> is None, all of the problem's solvers are returned."""

    if solver_strs is None:
        return problem.solvers, []

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


def print_outcome_line(solver, outcome_str):
    """Print a single line indicating the outcome of an action on a solver."""
    format_str = "{name:.<{name_len}}..{outcome_str:.>{outcome_len}}"
    format_values = dict(name=solver.__name__, name_len=SOLVER_NAME_MAX_LEN,
                         outcome_str=outcome_str,
                         outcome_len=OUTCOME_STR_MAX_LEN)
    print(format_str.format(**format_values))


def print_results(problem, solvers):
    if problem.solution is not None:
        print("Solution: {}".format(problem.solution))

    for solver in solvers:
        print_outcome_line(solver, get_result_str(problem, solver))

def get_result_str(problem, solver):
    try:
        result = solver(problem.actual_args)
    except MemoryError:
        return OUTCOME_STRS['MEMORY_ERROR']
    except Exception:    # tbd: timeout
        return OUTCOME_STRS['FAILED']

    if problem.solution is not None and result == problem.solution:
        return OUTCOME_STRS['CORRECT']
    elif isinstance(result, VALID_RESULT_TYPES):
        return str(result)
    else:
        return repr(result)


def print_solvers(problem, solvers):
    for solver in solvers:
        print(solver.__name__)


def print_correctness_tests(problem, solvers):
    pass  # tbd


def print_performances(problem, solvers):
    timers = [timingtools.SingleArgTimer(solver) for solver in solvers]

    for test_index, test in enumerate(problem.performance_tests):
        print("Performance test {}".format(test_index))

        new_timers = []

        for timer in timers:
            try:
                timing = timer.min_run_time(test, TARGET_TIME, TIMING_TIMEOUT,
                                            MAX_EXECUTIONS)
            except timingtools.Timeout:
                timing_str = OUTCOME_STRS['TIMEOUT']
            except MemoryError:
                timing_str = OUTCOME_STRS['MEMORY_ERROR']
            except timingtools.CalleeError:
                timing_str = OUTCOME_STRS['FAILED']
            else:
                format_values = dict(time=timing*1000,
                                     decimals=TIMING_MS_DECIMALS)
                timing_str = "{time:.{decimals}f}ms".format(**format_values)

                new_timers.append(timer)

            print_outcome_line(timer.func, timing_str)

        timers = new_timers


def parse_args():
    """Parse command-line arguments and return them in a Namespace object.

    The returned namespace has the following attributes:
     - <action>, a function that takes a problem and a list of solvers,
       performs an action on them and prints feedback to the user.
     - <problem_id>, the ID of the desired problem.  None means that all
       problems should be examined.
     - <solver_strs>, a list of strings indicating which solvers should be
       used.  None means that all solvers should be used."""

    actions_by_name = collections.OrderedDict([
        ('solve', print_results),
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
        problem_ids = range(1, LAST_PROBLEM_ID+1)
    else:
        if not 1 <= args.problem_id <= LAST_PROBLEM_ID:
            sys.exit("error: problem ID must be between 1 and {}"
                     .format(LAST_PROBLEM_ID))
        problem_ids = [args.problem_id]

    for problem_id in problem_ids:
        print_action(problem_id, args.action, args.solver_strs)

main()

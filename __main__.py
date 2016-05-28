import argparse
import collections
import numbers

import problems
import pytools
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


def print_action(action, problem_id, solver_strs=None):
    if not 1 <= problem_id <= LAST_PROBLEM_ID:
        print("Problem {} does not exist here.".format(problem_id))
        return

    try:
        problem = problems.get_problem(problem_id)
    except ImportError:
        print("Import of problem {} failed.".format(problem_id))
        return

    if problem.problem_id != problem_id:
        format_str = "Error: module {desired} contains problem {actual}."
        format_values = dict(desired=problem_id, actual=problem.problem_id)
        print(format_str.format(**format_values))
        return

    print("Problem {}".format(problem_id))

    solvers_to_use = get_solvers_to_use(problem, solver_strs)
    action(problem, solvers_to_use)

    print()


def get_solvers_to_use(problem, solver_strs=None):
    if solver_strs is None:
        return problem.solvers

    name_to_solver = {solver.__name__: solver for solver in problem.solvers}
    solvers = []
    for solver_str in solver_strs:
        new_solver = get_solver(name_to_solver, solver_str)
        if new_solver is None:
            format_str = "{!r} is not a valid solver for this problem."    # c'mon, printing in a get function? tbd. hint: exceptions
            print(format_str.format(solver_str))
            continue
        if new_solver not in solvers:
            solvers.append(new_solver)

    return solvers

def get_solver(name_to_solver, solver_str):
    return pytools.get_abbreviated(name_to_solver, solver_str.lower())


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
    """Parse command-line arguments and return them in a Namespace object."""

    actions_by_name = collections.OrderedDict([
        ('solve', print_results),
        ('list', print_solvers),
        # ('test', print_test_results),  # tbd
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
        problem_ids = [args.problem_id]

    for problem_id in problem_ids:
        print_action(args.action, problem_id, args.solver_strs)

main()

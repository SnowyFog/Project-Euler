import argparse
import collections
import numbers

import problems
import pytools
import timingtools


LAST_PROBLEM = 8

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


def print_outcome_line(solver, outcome_str):
    """Print a single line indicating the outcome of an action on a solver."""
    format_str = "{name:.<{name_len}}..{outcome_str:.>{outcome_len}}"
    format_values = dict(name=solver.__name__, name_len=SOLVER_NAME_MAX_LEN,
                         outcome_str=outcome_str,
                         outcome_len=OUTCOME_STR_MAX_LEN)
    print(format_str.format(**format_values))


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

def print_results(problem, solvers):
    if problem.solution is not None:
        print("Solution: {}".format(problem.solution))

    for solver in solvers:
        print_outcome_line(solver, get_result_str(problem, solver))


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


def print_solvers(problem, solvers):
    for solver in solvers:
        print(solver.__name__)


def get_solver(name_to_solver, solver_str):
    return pytools.get_abbreviated(name_to_solver, solver_str.lower())

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

def print_action(problem_no, action, solver_strs=None):
    if not 1 <= problem_no <= LAST_PROBLEM:
        print("Problem {} does not exist here.".format(problem_no))
        return

    try:
        problem = problems.get_problem(problem_no)
    except ImportError:
        print("Import of problem {} failed.".format(problem_no))
        return

    if problem.problem_no != problem_no:
        format_str = "Error: module {desired} contains problem {actual}."
        format_values = dict(desired=problem_no, actual=problem.problem_no)
        print(format_str.format(**format_values))
        return

    print("Problem {}".format(problem_no))

    solvers_to_use = get_solvers_to_use(problem, solver_strs)
    action(problem, solvers_to_use)

def get_default_action():
    return print_results

def get_action(action_str):
    if action_str is None:
        return get_default_action()

    return pytools.get_abbreviated(actions_by_name, action_str.lower())


def parse_args():
    """Parse command-line arguments and return them in a Namespace object."""

    parser = argparse.ArgumentParser(
        description="Examine solver functions for Project Euler problems.")

    parser.add_argument(
        'problem_no', nargs='?', type=int, metavar='problem',
        help="number of the problem to be examined")
    action_choices_str = ', '.join(actions_by_name)
    parser.add_argument(
        'action_str', nargs='?', metavar='action',
        help="desired action (choose from {})".format(action_choices_str))
    parser.add_argument(
        '-s', '--solvers', nargs='+', metavar='SOLVERS', dest='solver_strs',
        help="desired problem solver functions")

    return parser.parse_args()


actions_by_name = collections.OrderedDict([  # tbd: add testing
    ('solve', print_results),
    ('list_solvers', print_solvers),
    ('time_solvers', print_performances),
])


def main():
    """Let the user examine solvers via command-line arguments."""

    args = parse_args()

    if args.solver_strs and args.problem_no is None:
        print("You can only specify solvers if you also specify a problem.")
        return

    if args.problem_no is None:
        for problem_no in range(1, LAST_PROBLEM+1):
            print_action(problem_no, get_default_action(), None)
            print()
        return

    action = get_action(args.action_str)
    if action is None:
        format_str = "{input!r} is not a valid action. (choose from {choices})"
        format_values = dict(input=args.action_str,
                             choices=', '.join(actions_by_name))
        print(format_str.format(**format_values))
        return
    print_action(args.problem_no, action, args.solver_strs)

main()

import importlib


PROBLEM_ID_NUM_DIGITS = 3


class WrongProblemError(Exception):
    """Problem module contains problem with the wrong ID."""


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
    return '.p' + str(problem_id).zfill(PROBLEM_ID_NUM_DIGITS)

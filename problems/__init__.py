import importlib


PROBLEM_NO_NUM_DIGITS = 3


def get_problem(problem_no):
    relative_module_name = _get_relative_name(problem_no)
    try:
        module = importlib.import_module(relative_module_name, __name__)
    except ImportError:
        raise
    except Exception:
        raise ImportError
    return module.problem

def _get_relative_name(problem_no):
    return '.p' + str(problem_no).zfill(PROBLEM_NO_NUM_DIGITS)

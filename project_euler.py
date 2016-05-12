import pytools


class Problem:
    """Project Euler problem with parameters, solution and solvers."""

    def __init__(self, problem_no, actual_args_dict, *, solution=None,
                 domain=None, test_dicts=[], **kwargs):
        super().__init__(**kwargs)

        self.problem_no = problem_no
        self.get_args = pytools.defaults_tuple('ProblemArgs', actual_args_dict)
        self.actual_args = self.get_args()
        self.solution = solution
        self.domain = domain
        self.tests = [self.get_args(**test_dict) for test_dict in test_dicts]

        self.solvers = []
        self.list_as_solver = pytools.append_to(self.solvers)

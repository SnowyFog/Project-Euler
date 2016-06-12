import mathtools as mt
from problems import Problem


problem = Problem(
  problem_id=6,
  actual_args_dict=dict(max=100),
  solution=None,
)

@problem.list_as_solver
def main(args):
    sum_of_squares = sum(n**2 for n in range(args.max+1))
    square_of_sum = mt.arithmetic_series(args.max+1)**2

    return square_of_sum - sum_of_squares

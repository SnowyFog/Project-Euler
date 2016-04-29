from project_euler import Problem
import mathtools as mt


problem = Problem(
  problem_no=3,
  actual_args_dict=dict(number=600851475143),
  solution=None,
  test_dicts=[
    dict(),
  ],
)

@problem.list_as_solver
def main(args):
    return mt.item_by_index(mt.prime_factors(args.number), -1)

from project_euler import Problem
import mathtools as mt


problem = Problem(
  problem_no=7,
  actual_args_dict=dict(prime_index=10001),
  solution=None,
  test_dicts=[
    dict(),
  ],
)

@problem.list_as_solver
def main(args):
    return mt.item_by_index(mt.primes(), args.prime_index)
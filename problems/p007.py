import mathtools as mt
from problems import Problem


problem = Problem(
    problem_id=7,
    actual_args_dict=dict(prime_index=10001),
    solution=None,
)


@problem.list_as_solver
def main(args):
    return mt.item_by_index(mt.primes(), args.prime_index)

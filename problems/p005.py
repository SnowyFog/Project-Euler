import collections

import mathtools as mt
from problems import Problem


problem = Problem(
    problem_id=5,
    actual_args_dict=dict(max=20),
    solution=None,
)


@problem.list_as_solver
def main(args):
    factors_counter = mt.counter_union(mt.prime_factor_counter(n)
                                       for n in range(1, args.max+1))

    factors = (f**count for f, count in factors_counter.items())
    return mt.product(factors)

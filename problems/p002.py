import itertools

from project_euler import Problem
import mathtools as mt


problem = Problem(
  problem_no=2,
  actual_args_dict=dict(max=4*10**6),
  solution=4613732,
  test_dicts=[
    dict(),
    dict(max=10**5000),
  ],
)


# A fibonacci number is even iff its index is 0 (mod 3).

# A closed-form solution is hard to implement because of precision issues.

@problem.list_as_solver
def check_parity(args):
    fibonacci_numbers = mt.items_up_to(mt.fibonacci_numbers(), args.max+1)
    even_fibonacci_numbers = (fib for fib in fibonacci_numbers if fib % 2 == 0)
    return sum(even_fibonacci_numbers)

@problem.list_as_solver
def every_third(args):
    fibonacci_numbers = mt.items_up_to(mt.fibonacci_numbers(), args.max+1)
    even_fibonacci_numbers = itertools.islice(fibonacci_numbers, 0, None, 3)
    return sum(even_fibonacci_numbers)

@problem.list_as_solver
def without_summation(args):
    # Where F is the list of fibonacci numbers:
    #   F[3n + 2] = F[3n + 1] + F[3n] = 2*F[3n] + F[3n - 1] =
    #   = 2 * (F[3n] + F[3*(n-1)] + ... + F[3]) + 1
    # Therefore, F[3n + 2] // 2 is the sum of all even fibonacci numbers up to
    # 3n.

    fibonacci_numbers = mt.fibonacci_numbers()
    double_sum_so_far = 0
    while True:
        if next(fibonacci_numbers) > args.max:
            return double_sum_so_far // 2
        next(fibonacci_numbers)
        double_sum_so_far = next(fibonacci_numbers)

def closed_form(args):
    pass    # jeez, this is hard

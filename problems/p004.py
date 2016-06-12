import mathtools as mt
from problems import Problem


problem = Problem(
    problem_id=4,
    actual_args_dict=dict(num_digits=3),
    solution=None,
)


@problem.list_as_solver
def main(args):
    start = 10**(args.num_digits-1)
    stop = 10**args.num_digits

    products = (a*b for a in range(start, stop) for b in range(a, stop))
    palindromes = (n for n in products if mt.is_decimal_palindrome(n))
    return max(palindromes)

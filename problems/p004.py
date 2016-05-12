from project_euler import Problem
import mathtools as mt


problem = Problem(
  problem_no=4,
  actual_args_dict=dict(num_digits=3),
  solution=None,
  test_dicts=[
    dict(),
  ],
)

@problem.list_as_solver
def main(args):
    start = 10**(args.num_digits-1)
    stop = 10**args.num_digits

    products = (a*b for a in range(start, stop) for b in range(a, stop))
    palindromes = (n for n in products if mt.is_decimal_palindrome(n))
    return max(palindromes)

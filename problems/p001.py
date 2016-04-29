from project_euler import Problem
import mathtools as mt
import typetools as tt


problem = Problem(
  problem_no=1,
  
  actual_args_dict=dict(
    divisors=frozenset({3, 5}),
    stop=1000,
  ),
  
  solution=233168,
  
  domain=dict(
    divisors=tt.SetOf(tt.positive_int),
    stop=tt.natural_number,
  ),
  
  test_dicts=[
    dict(),
    dict(
      divisors=frozenset({2, 3, 17, 101}),
      stop=10**5,
    ),
    dict(
      divisors=frozenset({3, 4, 14, 19, 34, 49, 101}),
      stop=10**7,
    ),
  ],
)


@problem.list_as_solver
def iterator_based(args):
    def is_multiple(n):
        return any(n % d == 0 for d in args.divisors)
    
    multiples = (n for n in range(args.stop) if is_multiple(n))
    return sum(multiples)

@problem.list_as_solver
def add_each(args):
    total = 0
    for n in range(args.stop):
        if any(n % d == 0 for d in args.divisors):
            total += n
    return total

@problem.list_as_solver
def set_based(args):
    multiples = set()
    for divisor in args.divisors:
        multiples.update(range(0, args.stop, divisor))
    return sum(multiples)

@problem.list_as_solver
def cycle_based(args):
    cycle_len = mt.lcm(args.divisors)
    num_periods, leftover_part_len = divmod(args.stop, cycle_len)
    half_cycle_stop = cycle_len // 2
    extras_from_bottom = leftover_part_len <= half_cycle_stop
    extras_stop = leftover_part_len if extras_from_bottom else cycle_len - leftover_part_len + 1
    
    half_cycle = set()
    extras = set()
    for divisor in args.divisors:
        for multiple in range(0, half_cycle_stop, divisor):
            half_cycle.add(multiple)
            if multiple < extras_stop:
                extras.add(multiple)
    num_numbers_in_cycle = len(half_cycle) * 2 - cycle_len % 2
    
    period_bases_sum = mt.arithmetic_series(num_periods) * cycle_len * num_numbers_in_cycle
    addends_sum_per_period = (num_numbers_in_cycle-1) * cycle_len // 2
    period_addends_sum = addends_sum_per_period * num_periods
    periods_sum = period_bases_sum + period_addends_sum
    
    num_leftovers = len(extras) if extras_from_bottom else num_numbers_in_cycle - len(extras) + 1
    leftovers_bases_sum = num_leftovers * num_periods * cycle_len
    leftovers_addends_sum = sum(extras) if extras_from_bottom else addends_sum_per_period - (len(extras) - 1) * cycle_len + sum(extras)
    leftovers_sum = leftovers_bases_sum + leftovers_addends_sum
    
    return periods_sum + leftovers_sum

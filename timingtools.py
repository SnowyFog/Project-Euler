import abc
import contextlib
import gc
import itertools
import timeit


class Timeout(Exception):
    """A timeout has occurred."""

class CalleeError(StandardError):
    """An error has occurred when the callee was being executed."""


@contextlib.contextmanager
def run_without_gc(without_gc):
    if not without_gc:
        yield
        return
    gc_was_enabled = gc.isenabled()
    try:
        gc.disable()
        yield
    finally:
        if gc_was_enabled:
            gc.enable()


@contextlib.contextmanager
def handle_callee_error():    #tbd
    try:
        yield
    except MemoryError:
        raise
    except Exception:
        raise CalleeError


class Timer(object):
    """Measure the performance of something.
    
    Abstract base class."""
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, without_gc=True):
        """Initialize a timer instance."""
        self.without_gc = without_gc
    
    @abc.abstractmethod
    def single_run_time(self, timer=timeit.default_timer):
        """Return the run time of a single execution."""
    
    def min_run_time(self, target_time=None, timeout=None, max_executions=None,
                     timer=timeit.default_timer):
        """Return the minimum execution time.
        
        The execution time is measured multiple times for a single timing.  The
        total run time will be at most around <target_time> (measured in
        seconds) if it is not set to None.  A timeout occurs after <timeout>
        seconds if it is not set to None (tbd).  The execution time is measured
        at most <max_executions> times for a single timing if it is not set to
        None."""
        
        if target_time is timeout is max_executions is None:
            raise ValueError("at least one termination condition must be used")
        
        start_clock = timer()
        best_run_time = float('inf')
        with run_without_gc(self.without_gc):
            for _ in itertools.islice(itertools.repeat(None), max_executions):
                run_time = self.single_run_time(timer)
                if run_time < best_run_time:
                    best_run_time = run_time
                
                if target_time is not None:
                    time_so_far = timer() - start_clock
                    if time_so_far + run_time/2 > target_time:
                        break
        
        return best_run_time

class FuncTimer(Timer):
    """Measure the performance of a function.
    
    Abstract base class."""
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        super(FuncTimer, self).__init__(*args, **kwargs)


class NoArgTimer(FuncTimer):
    """Measure the performance of a function that takes no arguments."""
    
    def single_run_time(self, timer=timeit.default_timer):
        #tbd, docstring test
        func = self.func
        with handle_callee_error():
            start_clock = timer()
            func()
            end_clock = timer()
        return end_clock - start_clock

class SingleArgTimer(FuncTimer):
    """Measure the performance of a function that takes a single argument."""
    
    def __init__(self, *args, **kwargs):
        self.arg = None
        super(SingleArgTimer, self).__init__(*args, **kwargs)
    
    def single_run_time(self, timer=timeit.default_timer):
        func = self.func
        arg = self.arg
        with handle_callee_error():
            start_clock = timer()
            func(arg)
            end_clock = timer()
        return end_clock - start_clock
    
    def min_run_time(self, arg, *args, **kwargs):
        self.arg = arg
        return super(SingleArgTimer, self).min_run_time(*args, **kwargs)
        self.arg = None    # ugly, tbd

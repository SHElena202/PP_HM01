#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable(func):
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''

    return func


def decorator(func_decorator):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    def decorator_wrapper(func_decorated):
        return update_wrapper(decorator_wrapper(func_decorated),func_decorated)

    return decorator_wrapper


def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''

    def countcalls_wrapper(*args):
        countcalls_wrapper.calls += 1
        return func(*args)

    countcalls_wrapper.calls = 0

    return countcalls_wrapper


def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''
    def memo_wrapper(*args):
        if memo_wrapper.cached_calls.get(args):
            return memo_wrapper.cached_calls[args]
        else:
            memo_wrapper.cached_calls[args] = func(*args)
            return memo_wrapper.cached_calls[args]

    memo_wrapper.cached_calls = {}
    return memo_wrapper


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    def n_ary_wrapper(*args):
        if len(args) == 1:
            return args[0]
        return func(*args) if len(args) == 2 else func(args[0],n_ary_wrapper(*args[1:]))

    return n_ary_wrapper


def trace(filler):
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    #>>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''

    def wrap_orig_func(func):

        def trace_wrapper(*args):
            iter_filler = filler * trace_wrapper.iter_count
            print("{}--> {}({})".format(iter_filler, func.__name__, *args))
            trace_wrapper.iter_count += 1
            result_orig_func = func(*args)
            trace_wrapper.iter_count -= 1
            print("{}<-- {}({}) == {}".format(iter_filler, func.__name__, *args, result_orig_func))
            return result_orig_func

        f = trace_wrapper
        f.iter_count = 0
        return f

    return wrap_orig_func

@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()

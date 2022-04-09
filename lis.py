from io import StringIO
import os
import re
import readline as rl
import atexit
from copy import deepcopy, copy
from typing import *
from collections import namedtuple
import operator
from functools import reduce, lru_cache
import sys

# Get a string and yields tokens. There are
# three kinds of tokens "(", ")" and words.
# spaces are ignored
def tokenize(inp: str) -> Iterator[str]:
    i = 0
    cur = lambda: inp[i]
    empty = lambda: len(inp[i:]) == 0

    def word():
        nonlocal i

        s = StringIO()
        while not (empty() or cur().isspace() or cur() in "()"):
            s.write(cur())
            i += 1
        return s.getvalue()

    def skip_comment():
        nonlocal i
        assert cur() == ";"
        while cur() != "\n":
            i += 1

    while not empty():
        if cur() == ";":
            skip_comment()
        if cur().isspace():
            i += 1
        elif cur() in "()":
            yield cur()
            i += 1
        else:
            yield word()


# Gets an input iterator returned by tokenize() and
# return a nested list of strings. So for example
# _parse(tokenize("(foo (bar))")) returns ["foo", ["bar"]]
# the stack parmeter is to take account of unbalanced
# parenthesis
def _parse(inp_iter, stack=0):
    result = []
    for token in inp_iter:
        if token == "(":
            result.append(_parse(inp_iter, stack + 1))
        elif token == ")":
            return result
        else:
            result.append(token)

    if stack != 0:
        raise ValueError("unbalanced parenthesis")
    return result[0]


# easier to call
def parse(inp):
    return _parse(tokenize(inp))

# Gets an AST (a nested list) and return a string of that AST
def unparse(inp):
    if type(inp) is list:
        if not inp: # empty list
            return "()"
        s = StringIO()
        s.write("(")
        for arg in inp[:-1]:
            s.write(unparse(arg) + " ")
        s.write(f"{unparse(inp[-1])})")
        return s.getvalue()
    elif callable(inp):
        return inp.__name__
    elif type(inp) is closure:
        args = " ".join(inp.args)
        body = unparse(inp.body)
        return f"(lambda ({args}) {body})"
    else:
        return str(inp)



# When we see a (lambda (x) y) we generate a
# closure(x, y, env) where env is a copy
# of the current environment
closure = namedtuple("closure", "args body env")
setattr(closure, '__repr__', unparse)



# evaluates a expression, here inp is a
# nested list of strings already, env is a dict
def eval_(inp, env):
    if type(inp) is str:
        if inp.startswith(":"):
            # this is a keyword, return as it is
            return inp
        if inp == "env":
            return env
        try:
            # maybe this is an integer
            return int(inp)
        except ValueError:
            pass
        try:
            # or maybe is something in the environment
            return env[inp]
        except KeyError:
            pass
        # last attemp, something on global env
        try:
            return global_env[inp]
        except KeyError:
            pass

        print(f"Unbound variable {inp}")
        return None
    elif type(inp) is list:
        # if this is an empty list we do nothing
        if not inp:
            return None
        # this is a list, so we take the first argument
        # and evaluate until is not a list anymore
        op, *args = inp
        while type(op) is list:
            op = eval_(op, env)

        # then we call apply, op is our function, args
        # are the arguemnts and env is the environment
        # holding variables stuff
        return apply_(op, args, env)
    else:
        # Otherwise we just return the stuff as it is
        # this happens for numbers, constants like
        # True, False, None, and closures
        return inp


# apply a function to argumnts
def apply_(f, args, env):
    if f == "if":
        # (if cond then else)
        # evaluate the condition then
        # the 'then' or 'else' branch
        # depending on the condition
        cond, then, else_ = args
        if eval_(cond, env):
            return eval_(then, env)
        else:
            return eval_(else_, env)
    elif f == "lambda":
        # (lambda (args) body)
        # construct a closure
        args, body = args
        return closure(args, body, env)
    elif f == "define":
        sym, value = args
        env[sym] = eval_(value, env)
        return None
    elif type(f) is closure:
        # (<closure> args) ; <closure> is an evaluated (lambda (args) body)
        # okay this is a closure, here is how to call it

        # evaluate all the arguments befure calling, (scrict evaluation)
        args = (eval_(arg, env) for arg in args)

        # construct a list or pairs (argument, value)
        args_pairs = zip(f.args, args)

        # copy the environment, we pretend we're not using mutation
        newenv = copy(env)
        # update the environment with the closure environment
        newenv.update(f.env)
        # update the environment with the arguments, values pairs
        newenv.update(args_pairs)
        # evaluate the body with our new environment
        return eval_(f.body, newenv)
    elif type(f) is str and f in env:
        # (f args) ; but f is a user defined function
        # this is function in the environment
        # evaluate the arguments (strict evaluation),
        # apply the function and evaluate the result
        args = (eval_(arg, env) for arg in args)
        return eval_(apply_(env[f], args, env), env)
    elif f == "ignore":
        return None
    elif f == "prog":
        for arg in args[:-1]:
            eval_(arg, env)
        return eval_(args[-1], env)
    elif type(f) is str and f.endswith("!") and f in global_env:
        # a global macro, we treat ! specially here, just
        # call the macro passing the environment as last argument
        return eval_(global_env[f](*args, env), env)
    elif type(f) is str and f in global_env:
        # (g args) ; but g is a global defined function
        # the same as above but g is a global, like print
        args = (eval_(arg, env) for arg in args)
        return eval_(apply_(global_env[f], args, env), env)
    elif callable(f):
        # (<callable> args) ; callable comes after (g args) above
        # globals are callables so we need this branch to finally
        # call they
        args = (eval_(arg, env) for arg in args)
        return f(*args)
    else:
        # Don't know what to do
        raise RuntimeError(f"Dunno what to do with ({f} {args}) env keys = {list(env.keys())}")


# fix operator, with this is possible to use recursion
# with anonymous functions. your function need to take
# a continuation as last argument, for example (lambda (x cont) ...)
# then fix will call this function passing itself as
# the last argument, then function can then recurse
# by calling the continuation
#
# For example, this returns 120
# (fix (lambda (x k) (if (= x 0) 1 (* x (k (- x 1) k)))) 5)
def fix(f, *arg):
    return apply_(f, [*arg, f], {})


# A macro, I would like to be able to do let user do this
# but I have to change eval and apply functions to accommodate
# quoting.
#
# (let! (v arg) body) compiles to ((lambda (v) body) arg)
def let(arg, body, env):
    arg, v = arg
    v = unparse(v)
    arg = unparse(arg)
    body = unparse(body)
    result = f"((lambda ({arg}) {body}) {v})"
    return eval_(parse(result), env)


def assert_(x):
    assert x

# our global environment, everything here is a constant or a function
# you can extend the language by adding more globals
global_env = {
    "print": print,
    "true": True,
    "false": False,
    "nil": None,
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv,
    "%": operator.mod,
    "=": operator.eq,
    ">": operator.gt,
    "<": operator.lt,
    "<=": operator.le,
    ">=": operator.ge,
    "!=": operator.ne,
    "&": operator.and_,
    "|": operator.or_,
    "fix": fix,
    "let!": let,
    "env": print,
    "assert": assert_,
}


#  easier to call
def run(inp: str, env):
    return eval_(parse(inp), env)

# The REPL
def repl():
    # use readline lib for better input experience
    hist = os.path.join(os.path.expanduser("~"), ".lispy_history")
    try:
        rl.read_history_file(hist)
    except FileNotFoundError:
        pass

    atexit.register(rl.write_history_file, hist)
    prompt = "lispy"
    partial_inp = []
    env = {}

    def replace_last_history(inp):
        hlen = rl.get_current_history_length()
        rl.remove_history_item(hlen - 1)
        rl.add_history("\n".join(partial_inp) + "\n" + inp)

    def reset_prompt():
        nonlocal prompt
        prompt = "lispy"

    while (inp := input(f"{prompt}> ")) != "exit":
        try:
            if inp:
                if partial_inp:
                    print(run(" ".join(partial_inp) + " " + inp, env))
                    replace_last_history(inp)
                    reset_prompt()
                    partial_inp = []
                else:
                    print(run(inp, env))
                    reset_prompt()
        except ValueError as e:
            if str(e) == "unbalanced parenthesis":
                partial_inp.append(inp)
                prompt = "..."
        except Exception as e:
            import traceback

            print(f"Error {e}")
            print(traceback.format_exc())
        except KeyboardInterrupt:
            print("Keyboard interrupt, exiting")
            return

def main():
    if sys.stdin.isatty():
        return repl()
    else:
        return run(sys.stdin.read(), {})

if __name__ == "__main__":
    main()

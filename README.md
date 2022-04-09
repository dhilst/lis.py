# Small LISP interpreter in Python

#### THIS IS NOT SCHEME

## Constructs

The basic constructs of the language

* `(lambda (x) x)` : `lambda` keyword creates a lambda
* `(if true 1 0)` : `if` for `if` expressions
* `(fix (lambda (x k) (if (= x 0) x (k (- x 0)))) 2)`: `fix` for recursion, `fix` will take a lambda and call it passing it as the last argument. The `k`stand for continuation, is pretty common for use _k_ for continuation in the literature.
* `(define inc (lambda (x) (+ x 1)))`: `define` defines a symbol
* `env` returns the current environment, this is used for debugging as the object returned is a dict and _lispy_ has no means to work with Python dicts
* `; comment to the end of line` : use `;` for comments

## Constants and values

* `nil`is `None`
* `true`is `True` and `false` is `False`
* Integers are integers, no floats, sorry
* Symbol starting with `:` are called keywords and they evaluate to
  them selfs. You can think of it as constants
* We have no strings

## Global functions

* `print`, prints its argument, returns  `nil`
* `+ - * / %` are the arithemetic operations, pay attention that `/` is `//` in python or flordiv. Also, these functions that two arguments, calling with three or more will give you an error
* `= > < >= <= !=` are the boolean copmarisons
* `! &` bitwise operators
* `let!`, this is in fact a macro `(let! (x 1) (+ x 1))` expands to `((lambda (x) (+ x 1)) 1)`
* `(assert x)` : calls `assert x` in Python.
* `(ignore *args)` : Returns `nil` and don't evaluate the arguments. Use it for commenting code.
* `(prog *args)` : Evaluate all the arguments and return the last one. Note that `((foo x) (bar y))` means _Execute `(foo x)`, then apply it's result to `(bar y)`_. If you need _Execute `(foo x)`, ignore it's result and then execute `(bar y)`_ then you need to write `(prog (foo x) (bar y))`.

# REPL

If you execute `python3 lis.py`it will start the REPl, you can type the code and press enter to submit, if you have unbalanced parenthesis it will exibihit the prompt "...>". It uses `readline` library for better input experience, you should get history for free too, it creates the `~/.lispy_history` file, it's safe to delete this file if you want.

# Running files

If you redirect the input to `lis.py` it will interpret the whole thing as a single string and execute the code. It will not print intermediary resulst so you may want to use print to see the results.

# Motivation

1. I want something easy to tweak to pratice lambda calculus, so this
   is why we don't have anything other data type beside lambdas, you
   have to use lambdas to construct otherstuff :), this is functional
   programming in it's essence.
2. I want to try something where every logic is semantic, in regarding
   parsing there is only parenthesis and words.

# Common errors:

* `Dunno what to do with (k ...` when executing a recursive function, you probally forgot to call it using fix.

# Examples

You can check the `test.lispy` file for examples. You can the example
by `python3 lis.py < test.lispy`

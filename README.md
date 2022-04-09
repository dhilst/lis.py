# Small LISP interpreter in Python

#### THIS IS NOT SCHEME

This is a simple and small implementation of a LISP like
interpreter for lambda calculus pratice. It has no data
structures, everything has to be build with lambdas.

## Tutorial

The REPL can be started by executing the `lis.py`file like
`python lis.py`, it accepts multiple line input and
readline integration with history etc. You can also type
the contents in a file and execute it like this
`python lis.py < file.lispy`. The extension doesn't matter.

About the language, the basic construct is a lambda :

```scheme
(lambda (x) (+ 1 x))
```

Since this is a strict language we have `if` too, so
`not` function is defined like this :

```scheme
(lambda (x) (if x false true))
```

As you can see we have booleans, the basic values are
booleans, keywords (like `:foo`) and integers like `1234`.

Keywords behave like constants, you can use then when
you need to test something for equality. And we have `nil`
to represent absence of values.

```scheme
(= :foo :foo) ;; prints True in REPL
```

You can define global symbols with `define`

```scheme
(define not (lambda (x) (if x false true)))
```

And `let!` to define local variables

```scheme
(let! (x 1)
  (+ x x)) ;; x = 1 here
```

Also we have print, print returns `nil`.

```scheme
(print :hello-world)
```

And the arithmetic, boolean and bitwise operators, in that order :
`+`, `*`, `/`, `%`, `=`, `!=`, `>`, `<`, `>=` `<=`, `&`, `|`:

The `even?` function can be defined like this

```
(define even? (lambda (x) (= (% x 2) 0)))
```

We have `prog` that make the role of a block, it evaluates all its
arguments and return the result of the last one.

A trace function, that print and return it's input
can be defined like this

```scheme
(define trace (lambda (x)
	(prog
		(print x)
		x)))
```

We have `fix` to call anonymous functions recursively, so we
can call anonymous factorial like this : 

```scheme
(fix (lambda (x fact) (if (= x 0) 1 (* x (fact (- x 1) fact)))) 5)
```

The above example will print `120` on REPL. `fix` will receive a
function and call it passing itself as the last argument. Note that
normal recursion also works :

```scheme
(define fact (lambda (x)
	(if (= x 0)
		1
		(* x (fact (- x 1))))))
(fact 5)
```

Comments are done with `;` and span up to the end of the line.

```scheme
; this is a comment
```

And we have `assert` which is basically calls `assert` in Python

```scheme
(assert (= 1 1)) ;; print nothing, return nil
(assert false) ;; abort with AssertionError
```

Thats it, congratulations you learned _lis.py_! Check out
`test.lispy` for more examples.


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
  themselves. You can think of it as constants
* We have no strings

## Global functions

* `print`, prints its argument, returns  `nil`
* `+ - * / %` are the arithemetic operations, pay attention that `/` is `//` in python or flordiv. Also, these functions that two arguments, calling with three or more will give you an error
* `= > < >= <= !=` are the boolean copmarisons
* `| &` bitwise operators
* `let!`, this is in fact a macro `(let! (x 1) (+ x 1))` expands to `((lambda (x) (+ x 1)) 1)`
* `(assert x)` : calls `assert x` in Python.
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

You can check the `test.lispy` file for examples. You can the run example
by `python3 lis.py < test.lispy`

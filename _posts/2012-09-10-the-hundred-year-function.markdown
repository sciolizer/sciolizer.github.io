---
layout: post
title: "The Hundred-Year function"
date: 2012-09-10 17:25
comments: true
categories: [artificial intelligence]
---
What will programming languages look like one hundred years from now? Where
will all of those [wasted cycles](http://paulgraham.com/hundred.html) end up going?

I think it is safe to say that the programming language of the future, if it
exists at all, will involve some kind of artificial intelligence. This post
is about why I think that theorem provers will be standard in languages of the future.

``` haskell The hundred year function
solve :: (a -> Bool) -> Size -> Random (Maybe a)
```

This simple function takes two arguments. The first is a predicate
distinguishing between desirable (`True`) and undesirable (`False`) values for A.
The second is a size restriction on A (e.g. number of bytes).

The function returns a random value of A, if one exists, meeting two
constraints:

1. It satisfies the predicate.
1. It is no larger than the size constraint.

Also, the `solve` function is guaranteed to terminate whenever the predicate
terminates.

First I will try to convince you that the `solve` function is more important than any of your petty opinions about syntax, object-orientation, type theory, or macros. After that I will make a fool of myself by explaining how to build the `solve` function with today's technology.

Why it matters
--------------

It can find fix-points:

``` python "Put down fahrenheit," said the explorer. "I don't expect it to matter."
def c2f(temp):
  return temp * 9.0 / 5 + 32

def is_fixpoint(temp):
  return temp == c2f(temp)

print solve(is_fixpoint, 8) # outputs -40.0
```

It can invert functions:

``` python Crazy Canadians think 37 is hot.
def f2c(temp):
  return (temp - 32) * 5 / 9.0

print solve(lambda fahr: 37.0 == f2c(fahr), 8) # 100.0 IS hot!
```

It can solve [Project Euler](http://projecteuler.net/problem=9) problems:

``` python Problem 9
def is_pythagorean_triple(a, b, c):
  return a*a + b*b == c*c

def is_solution(triple):
  if len(triple) != 3: return False
  if sum(triple) != 1000: return False
  if !is_pythagorean_triple(*triple): return False
  return True

print solve(is_solution, 12)
```

It can check that two functions are equal:

``` python Programming interviews exposed
def the_obvious_max_subarray(A):
  answer = 0
  for start in range(0, len(A) - 1):
    for end in range(start + 1, len(A)):
      answer = max(answer, sum(A[start:end]))
  return answer

def the_fast_max_subarray(A):
  max_ending_here = max_so_far = 0
  for x in A:
    max_ending_here = max(x, max_ending_here + x)
    max_so_far = max(max_so_far, max_ending_here)
  return max_so_far

def differentiates(input):
  return the_obvious_max_subarray(input) != the_fast_max_subarray(input)

# Prints None if the two functions are equal for all
#   input sequences of length 5 and smaller.
# Otherwise prints a counter-example.
print solve(differentiates, 4 * 5)
```

So it's useful for detecting the introduction of bugs when you are optimizing things.

In fact, the solve function can find a more efficient implementation on your behalf.

``` python My computer is smarter than Kadane, if you'll just be patient.
def steps(algorithm, input):
  (_result, steps) = eval_with_steps(algorithm, input)
  return steps

def is_fast_max_subarray(algorithm):
  # Check that algorithm is equivalent to the_obvious_max_subarray
  if solve(lambda input: the_obvious_max_subarray(input) != eval(algorithm, input), 4 * 5):
    return False
  # Check that algorithm is faster than the_obvious_max_subarray
  for example in example_inputs:
    if steps(algorithm, input) > steps(the_obvious_max_subarray, input):
      return False
  return True

print solve(is_fast_max_subarray, 1000) # prints a function definition
```

The speed check is crude, but the idea is there.

Keeping the size constraint reasonable prevents the `solve` function from just creating a giant table
mapping inputs to outputs.

[Curry and Howard](http://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence) tell us that
programs and proofs are one and the same thing. If our `solve` function can generate programs, then it
can also generate mathematical proofs.

``` python Ten years too late for Uncle Petros
goldbach = parse("forall a > 2: exists b c: even(a) => prime(b) && prime(c) && b + c == a")

def proves_goldbach(proof):
  if proof[-1] != goldbach:
    return False
  for step in range(0, len(proof) - 1):
    if not proof[step].follows_from(proof[0:step]):
      return False
  return True

print solve(proves_goldbach, 10000)
```

If the proof is ugly, we can decrease the search size, and we will get a
more elegant proof.

The `solve` function can find bugs:

``` python Like fuzz testing, but more exhaustive
def does_not_go_wrong(input):
  result = eval(my_program, input)
  return not is_uncaught_exception(result)

print solve(does_not_go_wrong, 10000)
```

The `solve` function will never get people to stop arguing, but it will at least change the dynamic
vs static types argument from a pragmatic one to an artistic one.

One last example:

Test-driven development advocates writing tests which are sufficient to construct the missing
parts of a program. So why write the program at all?

``` python Beck's revenge
def passes_tests(patches):
  return unit_tests.pass(partial_program.with(patches))

patches = solve(passes_tests, 10000)
if patches:
  print partial_program.with(patches)
else
  print "Tests not passable within search space"
```

In fact, unit_tests can be replaced with any assertion about the desired program: e.g. that it type
checks under Hindley-Milner, that it terminates within a certain number of steps, that it does
not deadlock within the first X cycles of the program's execution, and so on.

Are you excited yet? Programming in the future is awesome!

Implementation
--------------

Always start with the obvious approach:

``` python Exhaustive search
def solve(predicate, size):
  for num in range(0, 2 ^ (size * 8) - 1):
    val = decode(num)
    if predicate(val):
      return val
```

Correct, but useless. If the predicate consisted of only one floating point operation, the Sequoia
supercomputer would take 17 minutes to solve a mere 8 bytes.

The complexity of `solve` is clear. The variable `num` can be non-deterministically chosen from the range in
linear time (`size * 8`), decode takes linear time, and predicate takes polynomial time in most of
our examples from above. So `solve` is usually in NP, and no worse than NP-complete as long as
our predicate is in P.

It's a hard problem. Were you surprised? Or did you get suspicious when the programmers of the
future started exemplifying godlike powers?<sup><a href="#godlike" name="1">1</a></sup>

Thankfully, a lot of work has been put into solving hard problems.

Today's sat solvers can solve problems with 10 million variables. That's 1.2 megabytes of search
space, which is large enough for almost all of the examples above, if we're clever enough. (The
Kadane example is the definite exception, since the predicate takes superpolynomial time.)

The [Cook-Levin theorem](http://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem) gives us a
procedure for writing the `solve` function more efficiently.

1. Imagine a large number of processors, each with its own memory, lined up and
connected so that the output state of each processor and memory becomes the input state of the next processor and memory.
The state of the entire assembly is determined solely by the state of the first processor. The state
of the whole system is static.
1. Represent each (unchanging) bit in the assembly with a boolean variable, and generate constraints
on those variables by examining the logic gates connecting the bits.
1. Assign values to some of the variables in a way that corresponds to the first processor containing
the machine code of the predicate.
1. Likewise, assign values so that the accumulator register of the last processor contains the value `True`.
1. Apply a sat solver to the variables and their constraints.
1. Extrapolate a solution by examining the first processor's total state.

I call this approach "solving the interpreter trace" because the imaginary processors act as an
interpreter for the predicate, and we ask the sat solver to trace out the processor execution.

The approach is elegant, but it has three major problems:

1. The formula given to the sat solver is enormous, even for small predicates and input sizes. (It's
polynomial, but the coefficient is large.)
1. The formula is highly symmetrical, which means the sat solver will perform a lot of redundant computation.
1. The meaning of bits in later processors is highly dependent on the value of bits in earlier
processors (especially if the predicate starts off with a loop). This will force our sat solver to
work a problem from beginning to end, even when a different order (such as end to beginning) would
be more intelligent.

We can get rid of these problems if we compile our predicate directly into a boolean formula.
Compilation is easy enough if our predicate contains neither loops nor conditionals.

``` python An example without loops or branches
def isReadableAndWriteable(x):
  y = x & 4
  z = x & 2
  a = y == 4
  b = z == 2
  return a && b
```

becomes

``` haskell The sat formula, assuming 3-bit values.
(y0 == x0 & 0) & (y1 == x1 & 0) & (y2 == x2 & 1) &
(z0 == x0 & 0) & (z1 == x1 & 1) & (z2 == x2 & 0) &
(a == ((y0 == 0) & (y1 == 0) & (y2 == 1)) &
(b == ((z0 == 0) & (z1 == 1) & (z2 == 0)) &
a && b
```

Actually conditionals aren't that hard either

``` python A contrived branching example
def predicate(x):
  b = isEven(x)
  if b:
    w = x & 7
  else:
    z = x & 2
    w = z << 1
  return w < 3
```

becomes

``` haskell The sat formula, again assuming 3-bit values.
(b == (x0 == 0)) &
(b -> ((w0 == (x0 & 1)) & (w1 == (x1 & 1)) & (w2 == (x2 & 1)))) &
(~b -> ((z0 == (x0 & 0)) & (z1 == (x1 & 1)) & (z2 == (x2 & 0)))) &
(~b -> ((w0 == 0) & (w1 == z0) & (w2 == z1))) &
(w2 == 0 & (w1 == 0 | w0 == 0))
```

A sat solver would immediately assign `w2` the value `0`. If we were solving over an interpretational
trace, `w2` wouldn't be a single variable, but would be one of two variables depending on whether
`b` was `True` or `False`.

By compiling the predicate, we have enabled the solver to work from end to beginning (if it so chooses).

Can we handle loops?

``` python A six is a
def is_palindrome(str):
  i = 0
  j = len(str) - 1
  while i < j:
    if str[i] != str[j]: return False
    i += 1
    j -= 1
  return True
```

One approach is to unroll the loop a finite number of times.

``` python A six is a six is a six is a
def is_palindrome(str):
  i = 0
  j = len(str) - 1
  if i < j:
    if str[i] != str[j]: return False
    i += 1
    j -= 1
    if i < j:
      if str[i] != str[j]: return False
      i += 1
      j -= 1
      if i < j:
        if str[i] != str[j]: return False
        i += 1
        j -= 1
        if i < j:
          _longer_loop_needed = True
          i = arbitrary_value() # in case rest of function depends on i or j
          j = arbitrary_value() # (It doesn't in this example.)
  return True
```

With branching and conditionals, we are turing complete. Function calls can be in-lined up until
recursion. Tail recursive calls can be changed to while loops, and the rest can be reified as
loops around stack objects with explicit push and pop operations. These stack objects will
introduce symmetry into our sat formulas, but at least it will be contained.

When solving, we assume the loops make very few iterations, and increase our unroll depth as
that assumption is violated. The solver might then look something like this:

``` python Solver for a predicate with one loop
def solve(predicate, size):
  unroll_count = 1
  sat_solver = SatSolver()
  limit = max_unroll_count(predicate, size)
  while True:
    unrolled = unroll_loop(predicate, unroll_count)
    formula = compile(unrolled)
    sat_solver.push(formula)
    sat_solver.push("_longer_loop_needed == 0")
    sol = sat_solver.solve()
    if sol: return sol
    sat_solver.pop()
    sol = sat_solver.solve()
    if sol == None: return None # even unrolling more iterations won't help us
    sat_solver.pop()
    if unroll_count == limit: return None
    unroll_count = min(unroll_count * 2, limit)
```

`max_unroll_count` does static analysis to figure out the maximum number of
unrolls that are needed. The number of unrolls will either be a constant
(and so can be found out by doing constant reduction within the predicate), or it
will somehow depend on the size of the predicate argument (and so an upper bound can be found by
doing inference on the predicate).

The solver is biased toward finding solutions that use fewer loop iterations, since each loop
iteration sets another boolean variable to `1`, and thus cuts the solution space down by half.
If the solver finds a solution, then we return it. If not, then we try again, this time allowing
`_longer_loop_needed` to be true. If it **still** can't find a solution, then we know **no** solution
exists, since `i` and `j` were set to arbitrary values. By "arbitrary", I mean that, at compilation
time, no constraints will connect the later usages of `i` and `j` (there are none in this example)
with the earlier usages.

I admit that this approach is ugly, but the alternative, solving an interpreter trace, is even more
expensive. The hacks are worth it, at least until somebody proves P == NP.

Some of the examples I gave in the first section used eval. Partial evaluation
techniques can be used to make these examples more tractable.

I've only talked about sat solvers. You can probably get better results with an smt solver or a
domain-specific constraint solver.

In thinking about this problem, I've realized that there are several parallels between compilers
and sat solvers. Constant reduction in a compiler does the same work as the unit clause heuristic
in a sat solver. Dead code removal corresponds to early termination. Partial evaluation reduces
the need for symmetry breaking. Memoization corresponds to clause learning. Is there a name for
this correspondance? Do compilers have an analogue for the pure symbol heuristic? Do sat solvers
have an analogue for attribute grammars?

Today
-----

If you want to use languages which are on the evolutionary path toward the language of the future,
you should consider C# 4.0, since it is the only mainstream language I know of that comes with
a built-in [theorem prover](http://msdn.microsoft.com/en-us/library/dd264808.aspx).

Update (2013-11-24):

I am happy to report that I am not alone in having these ideas. "Search-assisted programming",
"solver aided languages", "computer augmented programming", and "satisfiability based inductive
program synthesis" are some of the
names used to describe these techniques. [Emily Torlak](http://people.csail.mit.edu/emina/) has
developed an exciting language called
[Rosette](https://excape.cis.upenn.edu/documents/rosette_Emina.pdf), which is a dsl for creating
solver aided languages. [Ras Bodik](http://www.cs.berkeley.edu/~bodik/) has also done much work
combining constraint solvers and programming languages. The [ExCAPE](https://excape.cis.upenn.edu/)
project focuses on program synthesis. Thanks to [Jimmy Koppel](http://www.jameskoppel.com/) for
letting me know these people exist.

-----------------------

<sup><a href="#1" name="godlike">1</a></sup>: Even many computer scientists do not seem to appreciate how different the world would be if we
could solve NP-complete problems efficiently. **I have heard it said, with a straight face, that a
proof of P = NP would be important because it would let airlines schedule their flights better, or
shipping companies pack more boxes in their trucks!** One person who did understand was Gödel. In
his celebrated 1956 letter to von Neumann, in which he first raised the P versus NP question,
Gödel says that a linear or quadratic-time procedure for what we now call NP-complete problems
would have "consequences of the greatest magnitude." For such a procedure "would clearly indicate
that, despite the unsolvability of the Entscheidungsproblem, the mental effort of the mathematician
in the case of yes-or-no questions could be completely replaced by machines." But it would indicate
even more. If such a procedure existed, then we could quickly find the smallest Boolean circuits
that output (say) a table of historical stock market data, or the human genome, or the complete
works of Shakespeare. It seems entirely conceivable that, by analyzing these circuits, we could make
an easy fortune on Wall Street, or retrace evolution, or even generate Shakespeare’s 38th play. For
broadly speaking, that which we can compress we can understand, and that which we can understand we
can predict. -- [Scott Aaronson](http://www.scottaaronson.com/papers/npcomplete.pdf)


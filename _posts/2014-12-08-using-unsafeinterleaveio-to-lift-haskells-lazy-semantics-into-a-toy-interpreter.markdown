---
layout: post
title: "Using unsafeInterleaveIO to lift haskell's lazy semantics into a toy interpreter"
date: 2014-12-08 18:16:09 -0700
comments: true
categories: ["programming languages"]
---

The main challenge of writing a lazy interpreter is sharing structure: in
particular, making sure that an individual closure is not evaluated more
than once. Obvious but tedious solutions in Haskell include using `IORef`s and monadic
state. The interpreter below uses a completely different tactic: exploiting
`unsafeInterleaveIO`. All function arguments are evaluated "right away", but in the
context of an `unsafeInterleaveIO` (so, in fact, they are actually not evaluated
right away). With this hack, we get to write an interpreter which *looks*
like an interpreter for a strict functional language, but actually
behaves lazily (by lifting haskell's own lazy semantics into our interpreter).

[Interpreter.hs](https://github.com/sciolizer/lazy-interpreter/blob/master/Interpreter.hs)

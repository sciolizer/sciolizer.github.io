---
layout: post
title: "Power in the small, properties at large"
date: 2022-02-16 11:00:00 -0700
comments: true
categories: [composition]
---

The fight between imperative and functional programming is a special case of a
larger tradeoff, which Ted Kaminski describes as [power vs properties][1].

> You cannot create an abstraction without saying two things: what it is, and
> what it is not... You cannot make an abstraction more **powerful** without
> sacrificing some **properties** that you used to know about it. Necessarily.
> You
> cannot require a new **property** be true about an abstraction without
> sacrificing
> some of its **power** and flexibility. Always.

Mutable data structures are strictly more **powerful** than immutable data
structures (code that works on immutable data structures will also work on
mutable data structures), and mutability often offers a way to make an algorithm
more efficient. But of course, they have lost the valuable **property** of
immutability: you have to be careful which functions you let touch your mutable
data structure, lest your program become incorrect because of an unexpected
mutation.

The algorithm for determining whether a program is correct is
divide-and-conquer: a program is correct if its pieces are correct and its
pieces are glued together correctly. A piece is correct if its post-conditions
are true when its pre-conditions are true. The glue is correct if all
pre-conditions are true. Pre-conditions and post-conditions are of course
properties, and so properties are the means by which we determine, *at large*,
whether our programs are correct.

But properties get in our way *in the small*. The for-loop is more powerful than
left-fold. Any left-fold can easily be turned into a for-loop, but the converse
is not true. The left-fold has some nice properties: the number of iterations is
always the size of the traversed data structure, for example. But if, upon
revisiting a left-fold, I realize I need early termination in some cases, then
I will wish I had written the left-fold as a for-loop. The properties of a
left-fold were never that valuable to me in the first place: if the whole
for-loop
is just a few lines long, then I can **see** that it is correct.

This suggests a guideline to follow in choosing between power and properties.
When my code is small, I want powerful abstractions (e.g. mutable data
structures) and powerful compositions (e.g. for-loops). When my code is large,
and especially when it spans multiple files, I want abstractions with clear
properties (e.g. immutable data structures) and compositions with clear
properties (e.g. left folds).

James Hague writes about how functional programming ideals can make [simple
problems hard][2].

> Given a block of binary data, count the frequency of the bytes within it.

He points out that it's tricky to find an efficient implementation of this
problem that doesn't involve destructive updates, and questions whether
destructive updates are necessarily bad:

> If a local array is updated inside of an OCaml function, then the result
> copied to a non-mutable array at the end... it looks exactly the same as the
> purely functional version from the caller's point of view.

This is a perfect example of choosing power in the small and properties at
large.

[1]: https://www.tedinski.com/2018/01/30/the-one-ring-problem-abstraction-and-power.html
[2]: https://prog21.dadgum.com/41.html


---
layout: post
title: "Partial evaluation of fat languages"
date: 2014-04-28 18:01:18 -0700
comments: true
categories: ["partial evaluation", "programming languages"]
---

Language theory has always been my favorite part of computer science, and recently I have been playing around with partial evaluation. Creating an optimal, self-applicable specializer is really tricky. I thought that I was helping myself by working in a very minimal language, but this turned out to be counter-productive. It is easier to write a specializer in a language that has a large number of unnecessary primitives. The additional complexity of each primitive is very localized: just add another case to the giant switch statement, which does nothing more than "lift" the container language's primitive into the contained language, and is a small price to pay
for easing the coding of the *rest* of the specializer.

But that was not the only benefit! It turns out that having extra constructs also makes the binding-time analysis easier. (Binding-time analysis is the task of figuring out which parts of a program are static and which are dynamic for a given partial input.) An obvious example is booleans. Using church-encoded booleans is more minimal than having primitive booleans and an if-then-else construct, but analyzing the former is harder, since it requires analysis of higher-order functions, which usually requires writing a type-inference algorithm. Maps are another example. Lisp-style association lists seem like a natural approach, but, unless you do some very sophisticated analysis, the specializer will fail to recognize when the keys are static and the values are dynamic, and so
appromixate to marking the entire data structure as dynamic (which usually kills optimality). By making maps a primitive in the language, you can code especially for that scenario.

For anybody interested in partial evaluation, I highly recommend the
[Jones, Gomard, and Sestoft book](http://www.itu.dk/~sestoft/pebook/pebook.html).
It is extremely lucid in its exposition, not only of partial evaluation, but of many other analysis and transformational techniques. For instance, a year or so ago I was trying to understand abstract interpretation, but I could not find a succinct explanation of the algorithm anywhere. It turns out they provide one in chapter 15. They do it in only five pages, most of which is examples. Another example is supercompilation, which was opaque to me until I read Neil Mitchell's excellent paper on
[Supero](http://ndmitchell.com/downloads/paper-rethinking_supercompilation-29_sep_2010.pdf).
But if he hadn't written it, I could have turned to chapter 17 of the book, which incidentally also covers deforestation in the same breath. I think the only computer science book which I have revisited more frequently than this one is
[Norvig and Russell's book on artificial intelligence](http://aima.cs.berkeley.edu/).
Pierce's [Types and Programming Languages](https://mitpress.mit.edu/books/types-and-programming-languages) is a close 3rd.

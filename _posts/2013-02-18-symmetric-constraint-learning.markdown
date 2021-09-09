---
layout: post
title: "Symmetric constraint learning"
date: 2013-02-18 18:24:20 -0700
comments: true
categories: ["artificial intelligence", "constraint satisfaction", "machine learning"]
---

Suppose I have the following graph:

```
  /- B -\        /- G -\
 /       \      /       \
A -- C -- E -- F -- H -- J
 \       /      \       /
  \- D -/        \- I -/
```

And I'm trying to find a two-coloring for it. (i.e. I want to color each of the nodes black or white in such a way that directly connected nodes have opposite colors.)
Obviously any realistic constraint solver is going to solve this problem in linear time, since any assignment causes a propagation to the rest of the graph.
(e.g. `A` being black causes `B`, `C`, and `D` to be white which causes `E` to be black, `F` to be white, `G`, `H`, and `I` to be black, and
`J` to be white.)

But suppose (since this is just an illustration) my constraint solver doesn't maintain arc consistency, but it *does* do some kind of
constraint learning. Also, suppose that I already know some of the symmetry in this problem.
In particular, I know that `[A, B, C, D, E]` is symmetric with `[F, G, H, I, J]`.
(The constraint solver doesn't have to discover this symmetry; I know it in advance.)

The constraint solver might learn at some point that `A == E`, because it combines the constraint `A != B` with `B != E`.
It would be a shame if the constraint solver later also learned that `F == J`. It would be nice if it could learn
`F == J` at the *same time* that it learns `A == E`, since I have told it about the symmetry of the problem.

Notice that the learning is valuable even though the two halves of the problem have different assignments. (If `A` is black, then `F` is white.)

How can a constraint solver make these kind of inferences?

Here's my current solution:

A constraint satisfaction problem is a collection of variables and constraints. We declare an ordered subset `X` of variables as
isomorphic to a subset `Y` of variables if for every constraint involving only variables in X there is an identical constraint involving the
corresponding variables in `Y`. (Constraints involving variables both in `X` and around `X` are not required to have a corresponding constraint.)

It follows that if `X` and `Y` are isomorphic, then their corresponding subsets must also be isomorphic.

Whenever a constraint solver learns a constraint, it can add all of the isomorphic constraints to its collection of learned constraints.
There might even be a space optimization here, if I can find an appropriate lazy data structure, e.g. by allowing "abstract" constraints
in the solver's collection of learned constraints. The hard part is figuring out how to do watched literals.

Has this problem already been tackled?


Original post:
[https://www.reddit.com/r/artificial/comments/18rttb/symmetric_constraint_learning/](https://www.reddit.com/r/artificial/comments/18rttb/symmetric_constraint_learning/)

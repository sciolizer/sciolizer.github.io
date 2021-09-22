---
layout: post
title: "An example of why software composition is hard"
date: 2021-09-22 11:00:00 -0700
comments: true
categories: [composition]
---

Combining two concepts into a program is rarely as simple as 
`import A; import B;`. Almost always, when you combine two libraries, additional
code must be written to handle their interaction. The following example comes
from Wolfgang Scholz. I learned about it from the paper [An Overview of
Feature-Oriented Software Development][1], by Apel and Kästner.

Suppose one library provides us with the implementation of a singly linked list:

``` csharp
class ForwardList {
    ForwardNode first { get; set; }
    public virtual void push(ForwardNode n) {
        n.next = first; first = n;
    }
}
class ForwardNode {
    ForwardNode next { get; set; }
}
```

and another library provides us with the implementation of a reversely linked
list:

``` csharp
class ReverseList {
    ReverseNode last { get; set; }
    public virtual void shup(ReverseNode n) {
        n.prev = last; last = n;
    }
}
class ReverseNode {
    ReverseNode prev { get; set; }
}
```

We'd like to combine them to make a doubly-linked list. If our language had
multiple inheritance, a naive combination would look like this:

``` csharp
class List : ForwardList, ReverseList {}
```

This is problematic in at least three ways.

### Problem 1: Ambiguity around how to share state

Our merged `List` class does not contain a single list with two directions of
traversal.
It contains two lists:

``` csharp
class List : ForwardList, ReverseList {
    override ForwardNode first { get; set; }
    override ReverseNode last { get; set; }
}
```

Obviously we want to combine `ForwardNode` and `ReverseNode` into a single
class `Node`.

``` csharp
class Node : ForwardNode, ReverseNode {}
```

Ambiguity remains over when and how occurences of `ForwardNode` and
`ReverseNode` should be replaced. In the case of a doubly-linked list, replacing
all occurences gives us the state we want:

``` csharp
class List : ForwardList, ReverseList {
    Node first { get; set; }
    Node last { get; set; }
}
```

But, had we been combining circular lists, this would not have been enough.

``` csharp
class CircularList : ForwardCircularList, ReverseCircularList {
    Node first { get; set; }
    Node last { get; set; } // wrong!
}
```

We would have wanted the fields `first` and `last` to be combined into a single
field.

Conceivably, all of this ambiguity might be resolvable with a set of annotations
or language keywords that the programmer provides to specify exactly the
combination for which she is looking. But state is only one part of the
problem...

### Problem 2: Type incompatibility

Replacing all occurences of `ForwardNode` and `ReverseNode` with `Node`
violates the typing rules around inheritance. Our method signatures have become:

``` csharp
class List : ForwardList, ReverseList {
    override virtual void push(Node n) { /* ... */ }
    override virtual void shup(Node n) { /* ... */ }
}
```

The `Node`s in these signatures are in contravariant position, and so these
signatures are valid only when `Node` is a superclass of `ForwardNode` and
`ReverseNode`, not when it is a subclass! That is, any class that previously
operated on a `ForwardList` would make calls to
`push(ForwardNode node)`, and these calls would become invalid in cases where
the receiver is a `List`, because `List` does not accept `ForwardNode`s in its
`push(...)` method, unless that `ForwardNode` is actually a `Node`!

How might we resolve this problem? Just as in the previous problem, we could
attempt replacing all occurences of `ForwardList` with `List`. That is,
for every class `X` that uses a `ForwardList`, the language could generate
a class `XPrime` that uses `List`s and `Node`s instead of `ForwardList`s and
`ForwardNode`s. This would work in some, but not all cases. If
class `X` constructed instances of `ForwardNode` directly, for instance, how
should it
construct a `Node` directly? Where would we get a value `prev` to pass into
the constructor of `Node`?

### Problem 3: Emergent logic

Correct implementations of `push` and `shup` require additional logic that
did not occur in either `ForwardList` or `ReverseList`:

``` csharp
class List : ForwardList, ReverseList {
    override virtual void push(Node n) {
        if (first == null) {
            last = n;
        } else {
            first.prev = n;
        }
        super.push(n);
    }
    override virtual void shup(Node n) {
        if (last == null) {
            first = n;
        } else {
            last.next = n;
        }
        super.shup(n);
    }
}
```

`push(...)` now incorporates some of the logic from `super.shup(...)`, namely
the assignment `last = n`. Simiarly, `shup(...)` incorporates some of the
logic from `super.push(...)`. How would a programming language know that such
mixing needed to occur? Moreover, this borrowed code is conditioned on a null
check. Neither the null check, nor the code in the other path of the null check
existed in the implementations of
`ForwardList` and `ReverseList`!

Of our three problems, this one is the most vexing. Programming languages today
have a multitude of ways to compose code. We have gone well beyond function
application
and created inheritance, multiple inheritance, generic functions, mixins,
traits, classical
prototypes, lieberman-style prototypes, aspects, type
classes, [open extensible object models][2], [module expressions][3],
and the list goes on and on.
Yet none of these composition models avoid the need to write additional logic
when you combine a `ForwardList` and a `ReverseList`.

Still, it must be possible, because humans do it all the time. A promising
approach is to add constraints to our language, a la
[abstract data types][6]. In such a paradigm, we could omit the implementation
code, and instead provide constraints on our methods' behaviors:

```
class ForwardList {
    inferred void push(ForwardNode node);
    inferred ForwardNode get(int index);
    // ... extra methods ...
    constraint {
        free vars len : int, list : ForwardList;
        for (i : 0..len) {
            list.push(new ForwardNode());
        }
        for (i : 0..(len - 1)) {
            assert list.get(i).next == list.get(i + 1);
        }
    }
    // ... extra constraints ...
}

class ReverseList {
    inferred void shup(ReverseNode node);
    inferred ReverseNode get(int index);
    // ... extra methods ...
    constraint {
        free vars len : int, list : ForwardList;
        assume list.get(0) == null; // so that we start with an empty list
        for (i : 0..len) {
            list.push(new ReverseNode());
        }
        for (i : len..1) {
            assert list.get(i).prev == list.get(i - 1);
        }
    }
    // ... extra constraints ...
}
```

The beauty of constraints is that they compose perfectly. The composition of two
constraints is simply their conjunction! Combining the two types of list is now
straightforward:

```
class Node combines ForwardNode, ReverseNode {}
class List combines
        ForwardList[ForwardNode => Node],
        ReverseList[ReverseNode => Node] {
    // we receive push() from ForwardList
    // we receive shup() from ReverseList
    
    // we receive get() from both, and they become the same method because
    // their types have been coerced to Node.

    // we receive all of the constraints from ForwardList
    
    // and we receive all of the constraints from ReverseList
}
```

The constraints from `ForwardList` and `ReverseList` both call `get()`, and so
we
force our
sufficiently-smart compiler to derive new implementations of `push()` and
`shup()`.
The constraints ensure that it will be the implementation we desire.

Such a compiler might seem like magic now, but research is progressing toward
it. Current endeavors include [Rosette][7], [SynQuid][5], and the
[ExCAPE project][8]. And you can get a [surprising amount of mileage][9] out of
the
logic program `eval(Program, ...) := ...`.

[1]: https://www.cs.cmu.edu/~ckaestne/pdf/JOT09_OverviewFOSD.pdf
[2]: http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.121.6603&rep=rep1&type=pdf
[3]: https://en.wikipedia.org/wiki/OBJ_(programming_language)
[4]: https://www.kestrel.edu/research/specware/documentation/4.2/language-manual/SpecwareLanguageManual.pdf
[5]: https://www.youtube.com/watch?v=HnOix9TFy1A
[6]: https://en.wikipedia.org/wiki/Abstract_data_type
[7]: https://excape.cis.upenn.edu/documents/rosette_Emina.pdf
[8]: https://excape.cis.upenn.edu/
[9]: https://www.youtube.com/watch?v=fHK-uS-Iedc
---
layout: post
title: "Foreach mutation"
date: 2008-10-18 11:12
comments: true
categories: [binding,foreach,lexical closures]
---
Many languages have adopted some form of the "foreach" keyword, for traversing elements of a collection. The advantages are obvious: fencepost errors are impossible, and programs are easier to read. Foreach loops are not places where I expect to find bugs. But about a month ago, I found one, in a piece of code similar to the code below. The expected behavior of the program is to print out the numbers zero and one, on separate lines. Do not read past the end of the program if you want to find the bug yourself, because I explain it below.

{% include_code foreach-mutation/foreach.py %}

The solution has to do with the implementation of the for loop in python. (I ran the program in cpython; it may be interesting to see what other implementations of python do.) Rather than creating a new binding for the num variable on every iteration of the loop, the num variable is mutated (probably for efficiency or just simplicity of implementation). Thus, even though numclosures is filled with distinct anonymous functions, they both refer to the same instance of num.

I tried writing similar routines in other languages. Ruby and C# do the same thing as Python:

{% include_code foreach-mutation/foreach.rb %}

{% include_code lang:csharp foreach-mutation/foreach.cs %}

Please excuse the use of the NumClosure delegate. For some reason I could not get Mono to compile with Func<int>.

Fortunately, all of these languages provide some kind of work-around. Ruby has Array#each, and C# has List<>.ForEach. Python has the map built-in.

{% include_code foreach-mutation/foreach_rebind.py %}

{% include_code foreach-mutation/foreach_rebind.rb %}

{% include_code lang:csharp foreach-mutation/foreach_rebind.cs %}

Not everybody mutates their enumerators, however. Lisp, the language which normally requires every programmer to be an expert in variable scoping, handles iteration very cleanly:

{% include_code foreach-mutation/foreach.cl %}

And despite its messy syntax, Perl also scores a 10 for clean variable semantics:

{% include_code foreach-mutation/foreach.pl %}

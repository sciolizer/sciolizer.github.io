---
layout: post
title: "De-coupling interfaces with 'yield lambda'"
date: 2008-09-15 10:40
comments: true
categories: coroutine python
---
Though [separation of concerns](http://en.wikipedia.org/wiki/Separation_of_concerns) may be the most important design principle in software, its effective implementation is often elusive. A common problem in web design is how to link a sequence of pages together without scattering their logic all over the application. While this problem has been almost completely solved by continuation based web servers, not every language supports continuations. There is a middle ground however: coroutines. This post describes a light-weight approach to doing continuation-style web programming using Python’s coroutines.

Our target application will be the following "guess a number" game.

{% include_code yield-lambda/simple.py %}

Here is what the program looks like using coroutines:

{% include_code yield-lambda/game.py %}

Essentially, all read and write actions with the outside world have been replaced with the yield lambda pattern. That includes the call to rgen.randint, because rgen has been initialized according to the current time.

All we need now is an interface that implements the following methods:

``` python Interface
# displays the given text to the user and returns None
interface.display(text)

# displays the given text to the user and returns a string input by the user
interface.prompt_string(text)

# display the given text to the user and returns an int input by the user
interface.prompt_int(text)

# display the given text to the user and returns True for yes and False for no
interface.prompt_yes_no(text)
```

We’ll start with the simpler command line version:

{% include_code yield-lambda/cli.py %}

The behavior of cli.py + game.py is completely identical to simple.py. Remarkably, though, the core logic of the game (in game.py) is now re-usable with any user interface supporting the four methods given above.

A typical web-[MVC](http://en.wikipedia.org/wiki/Model-view-controller)-style solution to the "guess a number" game would probably have a controller which dispatched on one of three different situations: the user has input her name, the user has input a guess, or the user has told us whether or not she would like to keep playing. The three different situations would likely be represented as distinct URIs. In our game.py, however, a situation corresponds to the "yield lambda" at which execution has been paused.

The essential idea to writing a coroutine-based web interface is this: only run the game routine up to the point where more information is needed. Store the result of every lambda yielded so far. On successive page requests, replay the routine with the stored results, but only invoke the lambdas that were not invoked on a previous page request. The medium for storing the results of the lambdas does not matter. It could be embedded in hidden input elements in HTML (though this raises issues of trust), or stored in a database tied to a session ID. For simplicity, the following implementation stores the values in memory, tied to a value stored in a hidden input element.

{% include_code yield-lambda/web.py %}

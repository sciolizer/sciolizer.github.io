---
layout: post
title: "Faking continuation based web serving using exceptions"
date: 2008-10-04 11:01
comments: true
categories: [continuation,exception,python,separation of concern]
---
A friend has pointed out to me that the command line and web interface in my [last post](/blog/2008/09/15/de-coupling-interfaces-with-yield-lambda/) do not need to interact with the main game through an iterator. He proposed that the web interface could pause the execution of the game by using exceptions. I played with the idea, and discovered that he was right. The upshot is that continuation-based web serving can be faked in any language which has exceptions. (Lexical closures are also helpful, but can also be faked using objects.) The approach given below relies on neither CPS nor monads, and so has the added advantage of being fairly idiomatic in most mainstream languages.

As before, our game is the children's "Guess a number between 1 and 100" game:

{% include_code fake-continuation-server/game.py %}

I like this version much better because the ugly wart of before:

``` python The trouble with calling a generator from a generator
# The coroutine equivalent of self.__play_game()
iter = self.__play_game()
try:
    y = yield iter.next()
    while True:
        y = yield iter.send(y)
except StopIteration:
    pass
```

has been simplified to:

``` python Regular method invocation
self.__play_game()
```

The interface between the game and the user interface is the same as before, with one addition:

``` python Interface
display(text)       # displays the given text to the user and returns None
prompt_string(text) # displays the given text to the user and returns a string input by the user
prompt_int(text)    # display the given text to the user and returns an int input by the user
prompt_yes_no(text) # display the given text to the user and returns True for yes and False for no

get(callback)       # invokes the callback and returns what it returns
```

The new method "get" is made use of in the game when generating the answer for the game:

``` python Get usage
my_number = self.interface.get(lambda: rgen.randint(1,100))
```

Retrieving the random number through self.interface.get ensures that the game will not be constantly changing its answer while a user is playing through the web interface.

As before, the command line interface is very simple:

{% include_code fake-continuation-server/cli.py %}

The web interface works by raising a StopWebInterface exception when execution of the game needs to be paused so that the user can input some data into a form. Our abstraction is thus slightly leaky, in that a game which at some point generically caught all types of exceptions might interfere with the behavior of the web interface. The [yield lambda](/blog/2008/09/15/de-coupling-interfaces-with-yield-lambda/) solution did not have this problem.

{% include_code fake-continuation-server/web.py %}

---
layout: post
title: "Rubber-duck logging"
date: 2013-10-04 18:51:20 -0700
comments: true
categories: ["productivity"]
---

I often ask myself, "How can I be a more productive software engineer?" I can answer this question better if I break it down into pieces.

In my day to day work, there are approximately five things that take up most of my time. Ordered from most time consuming to least time consuming, they are:

1. Debugging
2. Writing code
3. Helping other people
4. Learning and evaluating libraries, frameworks, and tools
5. Designing solutions

So the obvious place to start is reducing my time spent debugging. The best way to reduce debugging time is to avoid doing it in the first place, and I've accomplished this a number of ways. From best to worst:

1. Using languages that have very strong type systems (e.g. haskell)
2. Using smart editors (e.g. IntelliJ) that give me immediate feedback when I make mistakes
3. Writing code in short, quick iterations instead of large batches
4. Writing unit tests

(To the weenies who are angry at me for putting unit tests at the bottom: it's only because I hit the point of diminishing returns once I've applied the other approaches. I found writing unit tests in ruby to be *enormously* helpful, because ruby is neither statically typed nor does it have smart editors. But when I'm writing scala in IntelliJ, the type system and the editor catch *so many* of my bugs that there's usually nothing left for the unit tests to find. I still write unit tests, but they provide more value in discovering regressions than in discovering bugs the first time around.)

Despite using all these approaches, debugging *still* takes up more of my time than the actual writing of the code. The only exception has been haskell, but I don't use haskell at work.

My approaches are fairly standard, but a few days ago I discovered an approach that I haven't heard described elsewhere. I was practicing the habit of "noticing when I'm surprised". Being frequently surprised is bad because it means I'm not learning. I noticed that sometimes when I ran my programs, they did not behave the way I expected. i.e. I was surprised.

How could I stop being surprised? I decided to start documenting my surprises. I created a document with a table of two columns. In the left column I would record each surprise: what I did, what I expected to happen, and what actually happened. In the right column I would record the resolution (once I had finished debugging it), and why my expectations were wrong in the first place.

I was hoping that after doing this for a few days, I would have enough data to find the persistent errors in my thinking. But something pleasant happened before I got that far!

I have not been very disciplined about this. I have only remembered to document my surprises twice since I started this experiment, and I almost missed the second one. I was about to bust out the printlns and the debugger before I caught myself. Although it felt tedious, I opened up my document and wrote down what I did, what I expected to happen, and what actually happened. When I added that last part, it suddenly hit me what my mistake was. No debugging necessary! Apparently the very act of articulating the difference between my expectations and reality was sufficient for me to recognize the error in my thinking (and my coding).

Perhaps it was a fluke. Perhaps the reason would have come to me anyway. But I am now definitely motivated to continue this experiment.

---
layout: post
title: "Automatic redis, part one: inserts and cache key extraction"
date: 2013-11-23 21:04:08 -0800
comments: true
categories: [artificial intelligence, automatic redis]
---
This post is part of a sequence I am calling
[automatic redis](/blog/categories/automatic-redis), which is my attempt to solve
the cache invalidation problem.

These are some initial thoughts on how to automate cache updates.
The question I want to answer is this: given a mapping from redis
keys to the queries that produce their values, how can I
infer which redis commands should be run when I add, remove, and update items in the collections
which are my source of truth?

The code in this post is psuedo-haskell. What appears to the left of an `=` sign is not
always a function, and the `.` is used for record field lookup as well as function
composition.

I'll start with a simple example. Suppose I run a website which is a task manager, and
I want to display on my website the number of users who
have signed
up for an account. i.e. I want to display `count users`. I don't want to count the entire collection
every time I add an item to it, so instead I keep the count in redis, and increment it whenever
a new account is created. Proving that [INCR](http://redis.io/commands/incr) is the right command
to send to redis is straightforward:

``` haskell
numUsers = count users
numUsers_new = count (users ++ [user])
numUsers_new = count users + count [user]
numUsers_new = numUsers + 1
-- INCR numUsers
```

Notice that when `count` distributes, it changes the plus operation from union (`++`) to 
addition (`+`).

Here is a similar example, this time storing the ids instead of a count.

``` haskell
userIds = map userId users
userIds_new = map userId (users ++ [user])
userIds_new = map userId users ++ map userId [user]
userIds_new = userIds ++ map userId [user]
userIds_new = userIds ++ [user.userId]
-- SADD userIds 65495
```

Obviously the appropriate redis command to use in this case is [SADD](http://redis.io/commands/sadd).

Filtering is also straightforward.

``` haskell
activeUserIds = map userId (filter (\x -> x.status == ACTIVE) users)
activeUserIds_new = map userId (filter (\x -> x.status == ACTIVE) $
  (users ++
  [user]))
activeUserIds_new = map userId (
  filter (\x -> x.status == ACTIVE) users ++
  filter (\x -> x.status == ACTIVE) [user])
activeUserIds_new =
  map userId (filter (\x -> x.status == ACTIVE) users) ++
  map userId (filter (\x -> x.status == ACTIVE) [user])
activeUserIds_new = activeUserIds ++ map userId (filter (\x -> x.status == ACTIVE) [user])
-- SADD activeUserIds 65495
```

Obviously a pipeline of `SADD`s will be correct, and the expression to the right
of the `++` gives my automatic cache system a procedure for determining which `SADD`
operations to perform. When the cache system gets the user object to be added, it
will learn that
the number of `SADD` operations is either
zero or one, but it doesn't have to know that ahead of time.

A computer can easily verify the above three proofs, as long as they are properly annotated.
But can I get
the computer to create the proof in the first place?

Rewriting the activeUserIds example to use function composition suggests one approach.

``` haskell
activeUserIds = (map userId . filter (\x -> x.status == ACTIVE)) users
activeUserIds_new = activeUserIds ++ (map userId . filter (\x -> x.status == ACTIVE)) [user]
```

In general, it seems that queries of the form

``` haskell
values = (f . g . h {- ... -}) entities
```

become

``` haskell
values_new = values `mappend` (f . g . h {- ... -}) [entity]
```

provided f, g, h, etc. all distribute over `mappend`. The actual value of `mappend` will determine
which redis operation to perform. Integer addition becomes `INCR`, set union becomes `SADD`,
sorted set union becomes [ZADD](http://redis.io/commands/zadd), list concatenation becomes
[LPUSH](http://redis.io/commands/lpush) or [RPUSH](http://redis.io/commands/rpush), etc. An
important monoid which may not be obvious is the Last
monoid (`mappend x y = y`), which becomes [SET](http://redis.io/commands/set).

So much for updates on constant cache keys. Parameterized cache keys are much more
interesting.

On my task manager website, I want to have one cache entry per user. The user's id
will determine the cache key that I use.

``` haskell
taskIds_'userId' = (map taskId . filter (\t -> t.owner == userId)) tasks
```

It's tempting to think of this definition as a function:

``` haskell
taskIds :: UserId -> [TaskId]
```

But an automatic caching system will not benefit from this perspective.
From it's perspective, the
input is a task object, and the output is any number of redis commands. The system has to implicitly
discover the `userId` from the task object it receives. The `userId` parameter of `taskIds.{userId}`
is therefore more like a logic variable (e.g. from prolog) than a variable in imperative or functional
languages.

The monoidal shortcut rule is still valid for parameterized redis keys.

``` haskell
taskIds_'userId'_new = taskIds_'userId' ++
  (map taskId . filter (\t -> t.owner == userId)) [task]
```

The caching system does not need to reduce this expression further, until it receives
the task object. When it does, 
it can evaluate the addend as an expression
in a functional-logical language (similar to [Curry](http://www-ps.informatik.uni-kiel.de/currywiki/)).

``` haskell
taskIds_'userId'_new = taskIds_'userId' ++
  (map taskId . filter (\t -> t.owner == userId)) [task]
taskIds_'userId'_new = taskIds_'userId' ++
  (map taskId (filter (\t -> t.owner == userId) [task]))
taskIds_'userId'_new = taskIds_'userId' ++
  (map taskId (if (\t -> t.owner == userId) task then
    task : filter (\t -> t.owner == userId) [] else
           filter (\t -> t.owner == userId) []))
taskIds_'userId'_new = taskIds_'userId' ++
  (map taskId (if task.owner == userId then
    task : filter (\t -> t.owner == userId) [] else
           filter (\t -> t.owner == userId) []))
```

Unfortunately at this point the goal becomes suspended. The cache system
can cheat a little by unifying
`task.owner == userId` with `True` and `False`.

In the true case, `userId` unifies with `task.owner`, which I'll say is 65495:

``` haskell
taskIds_65495_new = taskIds_65495 ++ (map taskId $
  if 65495 == 65495 then
    task : filter (\t -> t.owner == userId) [] else
           filter (\t -> t.owner == userId) [])
taskIds_65495_new = taskIds_65495 ++ (map taskId $
  if true then
    task : filter (\t -> t.owner == userId) [] else
           filter (\t -> t.owner == userId) [])
taskIds_65495_new = taskIds_65495 ++ (map taskId $
  task : filter (\t -> t.owner == userId) [])
taskIds_65495_new = taskIds_65495 ++ (map taskId [task])
taskIds_65495_new = taskIds_65495 ++ task.id
-- SADD taskIds_65495 ${task.id}
```

In the false case, `userId` remains unbound, but that's ok, because the expression reduces to a no-op:

``` haskell
taskIds_'userId'_new = taskIds_'userId' ++
  (map taskId (if false then
    task : filter (\t -> t.owner == userId) [] else
           filter (\t -> t.owner == userId) []))
taskIds_'userId'_new = taskIds_'userId' ++ 
  (map taskId (filter (\t -> t.owner == userId) []))
taskIds_'userId'_new = taskIds_'userId' ++
  (map taskId [])
taskIds_'userId'_new = taskIds_'userId' ++ []
-- nothing to do
```

In general, whenever the cache system's
goals become suspended, it can resume narrowing/residuation by picking a subexpression
with low multiplicity (e.g. booleans, enums) and nondeterministically
unifying it with all possible values.

Most of the time, each unification will result in either a no-op, or a redis command with all
parameters bound. An exception (are there others?)
is queries which affect an inifinite number of redis keys,
e.g. caching all tasks that do NOT belong to a user.

``` haskell
taskIds_'userId' = (map taskId . (filter (\t -> t.owner != userId))) tasks
```

This is clearly a bug, so the caching system can just log an error and perform no
cache updates.
It may even be possible for the caching system
to catch the bug at compile time by letting the inserted entity (e.g. a task)
be an unbound variable, and seeing if a non-degenerate redis command
with unbound redis key
parameters can
be produced.

This post has focused mostly on inserts and queries that fit the monoidal pattern. In
another post I'll take a look at deletes and queries which are not so straightforward.

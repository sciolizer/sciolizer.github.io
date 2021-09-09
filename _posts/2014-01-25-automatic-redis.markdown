---
layout: post
title: "Automatic redis, part two: sorting and data structures"
date: 2014-01-25 12:40:47 -0800
comments: true
categories: [artificial intelligence, automatic redis]
---

This post is part of a sequence I am calling
[automatic redis](/blog/categories/automatic-redis), which is my attempt to solve
the cache invalidation problem.

In my [previous post](/blog/2013/11/23/automatic-redis/), I demonstrated that a
library could infer cache update operations from database insert operations by performing
algebraic manipulations on the queries that define the cache keys. The algebraic
laws needed were the distribution laws between monoids. e.g. `count` distributes
over the `Set` monoid to produce the `Sum` monoid. A library could also
infer the arguments of the cache keys (e.g. `taskIds.{userId} -> taskIds.65495`) by
performing functional logical evaluation on the cache key's query. If the library's goal
became suspended during evaluation, it could proceed by unifying expressions
of low multiplicity with all possible values. For instance, if the goal for a filter
query became suspended, the library could proceed by considering the `true` and
`false` cases of the filter separately.

In this post I would like to talk about sorting and limiting, as well as flesh out some of
the data structures that might be used in an automatic redis library.

##### Set

`Set` is the simplest data structure,
and forms the foundation for two of our other collection types.

``` haskell
type Set a = Data.Set.Set
```

The monoidal operation for `Set` is simply set union.

##### List

`List` is a `Set` with an embedded sorting function. Tracking the sorting function
enables us to compute redis sorted set keys if necessary.

``` haskell
data List a b = (Ord b) => List (a -> b) (Set a)
```

A commonly used sorting function would be `x => x.modifiedDate`.

The monoidal operation for `List` is the merge operation from merge-sort, with
one restriction: the sorting functions of both lists must be the same
sorting function.

##### LimitedList

`LimitedList` is a `List` with an upper bound on its size.

```haskell
data LimitedList a b = (Ord b) => LimitedList Integer (List a b)
```

The length of the contained `List` must be less than or equal to the upper bound.
Tracking the length enables us to know how to trim cache entries, e.g.
when using the [ZREMRANGEBYRANK](http://redis.io/commands/zremrangebyrank) command.

The monoidal operation for `LimitedList` is to merge-sort the two lists and truncate
the result to the limit. Similarly to `List`, the library expects both lists to have
the same
upper limit.

##### First and Last

`First` and `Last` are essentially `LimitedList`s whose upper bound is `1`. Making
specialized types for singleton LimitedLists makes working with non-collection redis
data structures easier.

``` haskell
data First a b = (Ord b) => First (a -> b) (Maybe a)
data Last  a b = (Ord b) => Last  (a -> b) (Maybe a)
```

Although `First` and `Last` have the same representation, they have different monoidal
operations, namely `(x,y) => x` and `(x,y) => y`.

##### Maybe

The `Maybe` type is useful for queries that always generate a unique result (such
as lookup by primary key), and as such the `Maybe` type
does not need to contain a sorting function.

``` haskell
data Maybe a = Nothing | Just a
```

The monoidal operation is to pick `Just` over `Nothing`, but with the restriction
that both arguments cannot be `Just`s.

``` haskell
instance Monoid Maybe where
  Nothing  `mappend` Nothing  = Nothing
  Nothing  `mappend` (Just x) = Just x
  (Just x) `mappend` Nothing  = Just x
  (Just x) `mappend` (Just y) = error "This should never happen."
```

Collision of `Just`s can happen if the application developer misuses the `The` operation
(defined below). Unfortunately this error cannot be caught by an automatic redis
library, because
the library never actually computes the value of `mappend`. The library only
tracks monoidal types so that it can know what the final redis commands will
be.

Speaking of query operations, it's about time I defined them. But first...
one more monoid.

```haskell
data Sum = Sum Integer

instance Monoid Sum where
  mappend = (+)
```

## Query operations

Query operations are parameterized over an input type and an output type.

``` haskell
-- QO = Query Operation
data QO input output where
  -- The operations Where, Count, Sum, The, and SortBy are not concerned with the ordering
  -- of their input, so they can work on Sets, Lists, LimitedLists, Firsts, Lasts,
  -- and Maybes. In these constructor definitions, 'coll' can mean any of those types.
  -- A real implementation might have multiples versions of these query operations,
  --   e.g. WhereSet, WhereList, WhereLimitedList, ..., CountSet, CountList, etc.
  Where :: Expr (a -> Boolean) -> QO (coll a)       (coll a)
  Count ::                        QO (coll a)       Sum
  Sum   ::                        QO (coll Integer) Sum

  -- 'The' takes a collection which is expected to have no more than one element
  -- and extracts the element.
  The   :: QO (coll a) (Maybe a)

  -- SortBy converts any kind of collection into a List.
  SortBy :: (Ord b) => Expr (a -> b) -> QO (coll a) (List a)

  -- Limit, First, and Last, are defined for any (seq)uence:
  --   Lists, LimitedLists, Firsts, and Lasts.
  Limit :: Integer -> QO (seq a) (LimitedList a)
  First ::            QO (seq a) (First a)
  Last  ::            QO (seq a) (Last a)

  -- Mapping only works on Set!
  Select :: Expr (a -> b) -> QO (Set a) (Set b)

  -- Well technically Select also works on Maybe, but we'll make a separate
  -- query operation for Maybes.
  Apply :: Expr (a -> b) -> QO (Maybe a) (Maybe b)

  -- Lists contain their sorting function, so we cannot allow arbitrary
  -- mapping on lists. We can, however, support monotonic mappings.
  SelectMonotonic        :: Expr (a -> b)          -> QO (seq a) (seq b)

  -- Mappings which scramble the order are also allowed, as long as we
  -- have a way to recover the order. i.e. 'a -> c' has to be monotonic,
  -- even though 'a -> b' and 'b -> c' do not.
  SelectReversible       :: Expr (a -> b) -> Expr (b -> c) -> QO (seq a) (seq b)
```

A few more data structures and we will have all the pieces necessary for
an application developer to define a cache schema.

``` haskell
data Table t = Table String

-- A Query is a sequence of query operations that begins with a table
data Query output where
  From :: Table t -> Query (Set t)
  Compose :: Query input -> QO input output -> Query output

-- convenience constructor
(+>) = Compose

data CacheKeyDefinition = CacheKeyDefinition {
  keyTemplate :: String, -- e.g. "taskIds.{userId}"
  query :: Query -- e.g. from tasks where task.userId = userId select task.id
}

```

Putting it all together, we can showcase the cache schema for a simple task management
website.

```haskell

type TaskId = String
type UserId = String

data Task = {
    taskId :: TaskId,
    ownerId :: UserId,
    title :: String,
    completed :: Boolean,
    dueDate :: Integer }
 deriving (Eq, Ord, Read, Show)

taskTable = Table "tasks" :: Table Task

schema = do
  -- The task objects.
  -- type: String
  -- expected redis commands on insert:
  --   SET
  "task.{taskId}" $= \tid ->
    From taskTable +>
    Where (\t -> taskId t == tid) +>
    The +>
    Apply show

  -- For each user, the ids of her most urgent tasks.
  -- type: Sorted Set, where the keys are the dueDate and the values are the taskIds.
  -- expected redis commands on insert:
  --   ZADD
  --   ZREMRANGEBYRANK
  "activeTaskIds.{userId}" $= \uid ->
    From taskTable +>
    Where (\t -> ownerId t == uid && not (completed t)) +>
    SortBy dueDate +>
    Limit 100 +>
    SelectReversible (\t -> (dueDate t, taskId t)) fst

  -- The number of tasks a user has successfully completed.
  -- type: integer
  -- expected redis commands on insert:
  --   INCR
  "numCompleted.{userId}" $= \uid ->
    From taskTable +>
    Where (\t -> ownerId t == uid && completed t) +>
    Count
```

It's important to keep in mind that although I have made the above code look
like haskell, no library in haskell could actually use the above code. The variables
occuring after the `$=` sign are logic variables, not function parameters. An
EDSL could get close to something like the above, but the normal types for
`==` and `&&` are unusable, and the lambdas inside the `Where` clauses
would need to be reified anyway.

Still to come: deletes, updates, uniqueness constraints (maybe?), and psuedo-code
for the generation of redis commands.

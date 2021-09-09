---
layout: post
title: "Automatic redis through static differentiation"
date: 2015-03-01 15:29:00 -0800
comments: true
categories: [flexible competence, automatic redis]
---

A new project,
"[Incremental λ-Calculus](http://www.informatik.uni-marburg.de/~pgiarrusso/ILC/)",
obviates my previous posts on [automatic redis](/blog/categories/automatic-redis).
The team has created an algorithm, called static differentiation, which performs a
source to source translation on functions in the simply typed lambda calculs.
The resulting function takes twice as many arguments as the previous program, with every
other argument being a diff, or derivative, on the previous argument. When further
optimizations are applied to the source, such as constant reduction and dead code elimination,
the non-derivative
arguments can sometimes be removed entirely. Here is an example from the paper:

``` haskell
type MultiSet = Map String Nat

-- | grandTotal counts the number of elements in each set and adds them
grandTotal :: MultiSet -> MultiSet -> Nat
grandTotal xs ys = fold (+) 0 (merge xs ys) where

-- Imported:
fold :: (Nat -> Nat -> Nat) -> Nat -> MultiSet -> Nat
(+) :: Nat -> Nat -> Nat
0 :: Nat
merge :: MultiSet -> MultiSet -> MultiSet
```

After static differentiation, the code becomes:<sup><a href="#imprecise" name="1">1</a></sup>

``` haskell
-- The derivative of a natural number is an integer, since
-- the natural number can either increase or decrease.
type Nat' = Int

type MultiSet' = Map String Nat'

grandTotal' :: MultiSet -> MultiSet' -> MultiSet -> MultiSet' -> Nat'
grandTotal' xs xs' ys ys' =
  fold' (+) (+') 0 (derive 0) (merge xs ys) (merge' xs dxs ys dys) where

-- Imported:
fold' :: (Nat -> Nat -> Nat)
      -> (Nat -> Nat' -> Nat -> Nat' -> Nat')
      -> Nat -> Nat'
      -> MultiSet -> MultiSet'
      -> Nat'
(+) :: Nat -> Nat -> Nat
(+') :: Nat -> Nat' -> Nat -> Nat' -> Nat'
0 :: Nat
derive :: Nat -> Nat'
merge :: MultiSet -> MultiSet -> MultiSet
merge' :: MultiSet -> MultiSet' -> MultiSet -> MultiSet' -> MultiSet
```

When optimizations are applied, `grandTotal'` becomes the implementation
that a programmer would have written:

``` haskell
grandTotal' :: MultiSet' -> MultiSet' -> Int
grandTotal' xs' ys' = fold' (+) 0 (merge' xs' ys')

-- Imported:
fold' :: (Int -> Int -> Int) -> Int -> MultiSet' -> Int
(+) :: Int -> Int -> Int
0 :: Int
merge' :: MultiSet' -> MultiSet' -> MultiSet'
```

In this case, the resulting `grandTotal'` makes no reference to the original multisets at all.
The authors of the paper call this "self-maintainability", by analogy to self-maintainable
views in databases.

The problem of infering redis update operations from database update operations, then,
is simply a matter of differentiating and then optimizing the cache schema. ("Cache schema" is
the mapping from redis keys to the database queries that populate those keys.)
The mappings whose derivatives are self-maintainable can be translated into redis commands.

Here is the source transformation described in the paper:

{% include_code static-differentiation/Differentiate.hs %}

Returning to an example from the [first post](/blog/2013/11/23/automatic-redis/):

``` haskell
userIds :: RedisSet
userIds = setToRedisSet (mapProjection userId (dbTableToSet usersTable))

setToRedisSet :: Set Id -> RedisSet
mapProjection :: (User -> Id) -> Set User -> Set Id
userId :: User -> Id
dbTableToSet :: DbTable User -> Set User
usersTable :: DbTable User
```

The derivative is

``` haskell
userIds' :: RedisSet'
userIds' = setToRedisSet' (mapProjection userId (dbTableToSet usersTable)) (mapProjection' userId userId' (dbTableToSet usersTable) (dbTableToSet' usersTable usersTable'))

setToRedisSet' :: Set Id -> Set' Id Id' -> RedisSet'

mapProjection  :: (User -> Id) ->                           Set User ->                    Set Id
mapProjection' :: (User -> Id) -> (User -> User' -> Id') -> Set User -> Set' User User' -> Set' Id Id'

userId  :: User ->          Id
userId' :: User -> User' -> Id'

dbTableToSet  :: DbTable User ->                        Set User
dbTableToSet' :: DbTable User -> DbTable' User User' -> Set' User User'

usersTable  :: DbTable User
usersTable' :: DbTable' User User'

data RedisSet' = SAdd String | ...
data DbTable' a a' = Insert a | ...
```

In the case of an insert, we have

``` haskell
usersTable' = Insert user
```

which means that `userIds'` can be reduced to

``` haskell
userIds' :: RedisSet'
userIds' = SAdd (userId user)
```

-----------------------
<sup><a href="#1" name="imprecise">1</a></sup>: I'm being a little imprecise when I define
the derivative of a type as another type, since the type of the derivative can vary
depending on the value. The derivative of 3 is all integers from -3 to positive infinity,
not all integers.

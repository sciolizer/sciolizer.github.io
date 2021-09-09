---
layout: post
title: "A data representation language"
date: 2013-05-06 18:58:50 -0700
comments: true
categories: ["programming language"]
---

I have an idea for a language, and I want to know if it already exists.
The language is a data representation language. It encodes rules about how data is represented in a store
(e.g. MySQL, HBase, Riak, Neo4J, MongoDB, Redis, flat files).
The language would have four directives: `entity`, `predicate`, `operation`, and `realize`.
The `entity` directive gives the "platonic" description of a type.

```
entity User
  Id id
  String userName
  String displayName

entity Task
  Id id
  String name
  Date dueDate

entity UserTask // encodes many-to-many relationship
  Id id
  User user
  Task task

entity Comment
  Id id
  Task parentTask
  String comment
  Date when
```

The `predicate` directive tells how these types are represented. For example, to represent the user object in a relational
database:

```
import RDBMS

predicate forall u: User exists r: RelationalRow where
  r.table = 'User' and
  r['id'] = u.id and
  r['userName'] = u.userName and
  r['displayName'] = u.displayName
```

or in a key value store:

```
import KeyValue
import Pickle

predicate forall u: User exists p: KeyValuePair where
  p.key = "User." + u.id.toString() and
  p.value : Pickled<Map<String,String>> and
  p.value['userName'] = u.userName and
  p.value['displayName'] = u.displayName
```

You can also use predicates to specify how types are embodied in classes.

```
predicate forall u: User exists o: Object where
  o.class = 'org.example.myapp.objects.User' and
  o['id'] = u.id and
  o['displayName'] = u.displayName
```

Notice that I left out `userName`; classes do not have to be perfectly aligned with the platonic entities. You can even combine
different entities into a single class. For example, imagine a Java class like this:

```
public class Task {
  public long id;
  public String name;
  public Date dueDate;
  public List<Comment> comments;
}
```

Even though tasks and comments are separate entites, you can still map between them and the task class:

```
predicate forall t: Task exists o: Object where
  o.class = 'org.example.myapp.objects.Task' and
  o['id'] = t.id and
  o['name'] = t.name and
  o['dueDate'] = dueDate and
  o['comments'] : List and
  o `sortedBy` (c => c['when']) and
  forall c: Comment (c.parentTask = t =>
    exists co: Object where
    co `in` o['comments'] and
    co.class = 'org.example.myapp.objects.Comment' and
    co['id'] = c.id and
    co['when'] = c.when
    co['comment'] = c.comment) and
  forall co: Object (co `in` o['comments'] =>
    exists c: Comment where
    c.parentTask = t and
    c.id = co['id'])
```

It's a little crazy, but it could be made simpler with a library function and/or syntactic sugar saying "this embodied list matches this list of entites". I just wanted to give you some idea of how flexible I want this language to be.

The `operation` directive gives names to operations that might be performed on the entities.

```
operation createUser(userName: in String, displayName: in String) where
  exists u: User and
  u.userName = userName and
  u.displayName = displayName and
  u.id `notIn` Before.User and
  After.User = Before.User + u

operation getTasksForUser(userId: in Id, tasks: out Set<Task>) where
  exists u: User where u.id = userId => (
  forall t: Task (exists ut: UserTask where
      ut.user = u and
      ut.task = t =>
    ut.task `in` tasks) and
  forall t: Task (t `in` tasks =>
    exists ut: User where ut.user = u and ut.task = t))
```

The `realize` directive indicates how operations will be realized using concrete classes.

```
realize createUser as
  void createUser(userName: java.lang.String, displayName: java.lang.String)

realize getTasksForUser as
  java.util.Set<org.example.myapp.objects.Task> getTasksForUser(u: org.example.myapp.objects.User)
```

Compiling would generate a code block for each `realize` directive. It would fail if any of the operations were impossible.
(e.g. `getTasksForUser` would be impossible for a key-value store if you had stored only 
`Task => [User]` pairs and forgotten the `User => [Taks]` pairs. It would generate a warning if any of the operations were slow.
(e.g. `getCommentsForTask` on an ordered key-value store when the comments were indexed by `commentId` and not by `$taskId:$commentId`)

So, does a language like this already exist? I know there are several things that come close, ORMs being the obvious example. Most ORMs require you to build schemas according to THEIR rules, not your own rules, and the exceptional ones require you to
write custom code, usually 4 different times, for the get, set, update, and delete cases, when the representation is anything
non-standard.

I want something that can handle

* multiple stores simultaneously, e.g. memcache and MySQL.
* denormalized data. e.g. if I have a User-to-Task and a Task-to-User representation of `UserTask` in a sharded database, the code generated for `createUserTask` should do two inserts.
* other really crazy representations, such as
  * In a column family database, storing the first comment of a task in the `comment1` column of the row for that task, the second comment in the `comment2` column, etc.
  * Putting a sentinel value in a redis list so I can tell the difference between an empty list and `unknown`.

Since it seems really useful, I would love to write this language, but honestly, I don't even know where to begin.
Conceptually, how do you translate quantified logic into imperative code? What would abstraction look like in this language?
(e.g. Can I make a `listEqualsList` function?) Outside of the `entity`/`predicate`/`operation`/`realize` directives, what
primitives would I need to provide so that other people can write modules for their favorite pet database?

---
layout: post
title: "The History of the Frame Problem"
date: 2017-03-05 18:56:43 -0700
comments: true
categories: [history, artificial intelligence, frame]
---

This is my synopsis of the paper, "[The History of the Frame Problem](https://staff.fnwi.uva.nl/b.bredeweg/pdf/BSc/20032004/KamermansSchmits.pdf)".

In 1969, McCarthy and Hayes tackled the problem of making agents that can formulate strategies to complete goals. The problem has two parts: representing the state of the world at various moments in time, and searching for a sequence of actions whose final world state satisfies the goal. Like good software engineers, they aspired to decouple the parts, and had a clever idea. They formalized in first-order logic

1. the initial state of the world
2. the preconditions under which an action can be taken, and
3. the state-to-next-state transformation an action produces on the world.

This solved the first half of the problem, and now the second problem could be solved by a generic theorem prover. Unfortunately, in practice, formalization #3 ended up being really large.

> We were obliged to add the hypothesis that if a person has a telephone, he still has it after looking up a number in the telephone book. If we had a number of actions to be performed in sequence, we would have quite a number of conditions to write down that certain actions do not change the values of certain fluents [fluent = a proposition about the world which changes over time]. In fact, with `n` actions and `m` fluents, we might have to write down `n*m` such conditions.

They called this problem of `n*m`-blowup the _frame problem_, but made the mistake of including the word _philosophical_ in the title of their paper, provoking AI doomsayers to cite it as yet another example of why computers could never think like humans. The discussion became more interesting when Daniel Dennett directed the attack away from the AI researches and toward the philosophers. He caricatured epistemology as a comically profound but very incomplete theory, because for thousands of years, no one had ever noticed the frame problem.

> ... it is turning out that most of the truly difficult and deep puzzles of learning and intelligence get kicked downstairs by this move [of leaving the mechanical question to some dimly imagined future research]. It is rather as if philosophers were to proclaim themselves expert explainers of the methods of a stage magician, and then, when we ask them to explain how the magician does the sawing-the-lady-in-half trick, they explain that it is really quite obvious: the magician doesn't really saw her in half; he simply makes it appear that he does. 'But how does he do that?' we ask. 'Not our department', say the philosophers - and some of them add, sonorously: 'Explanation has to stop somewhere.'

Some philosophers and AI researches argued that the original mistake leading to the frame problem was McCarthy and Hayes choosing first-order logic for world representation. Their case is easily made with the Tweety Bird problem: The premises

1. All birds fly
2. Tweety is a bird
3. All broken-winged creatures cannot fly, and
4. Tweety has a broken wing

can prove both

<ol start="5">
  <li>Tweety can fly, and</li>
  <li>Tweety cannot fly</li>
</ol>

Clearly premise 1 is too strong, but attempting to modify first-order logic to support _most_ statements instead of _all_ statements breaks monotonicity: Under _most_-enabling logic, premises 1, 2, 3 would prove 5, but premises 1, 2, 3, 4 would prove 6. An agent learning premise 4 would change its mind from conclusion 5 to conclusion 6. This is, of course, the desired behavior, but dropping the stability of truth means the agent can no longer use a generic theorem prover. The agent is using a modified logic system, and so it must use a specialized theorem prover. The question becomes: which logic system to use?

In standard first-order logic, every proposition is either true, false, or unknown. Learning new information can only ever change the status of unknown statements. To solve the tweety bird problem, a logic must enable assuming unknowns as false until proven otherwise (closed-world assumption). The symbolic AI community eventually converged on circumscription, which is a logic that assumes particular propositions to be false until proven otherwise.

McCarthy updated his situation calculus by circumscribing the proposition _Abnormal_, allowing him to formalize _Most birds fly_ as _All birds fly unless they are abnormal_ and adding the premise _Broken-winged creatures are abnormal._ Since the _Abnormal_ proposition is assumed to be false until proven otherwise, Tweety is assumed to be a normal flying bird until the agent learns that Tweety has a broken wing.

Shanahan took a time-oriented approach instead. In his circumscriptive event calculus, he circumscribed _Initiates_ and _Terminates_, so he could formalize _Most birds fly_ as _All birds can fly at birth_ and he could replace _All broken-winged creatures cannot fly_ with _Breaking a wing Terminates the flying property._ Since the _Terminates_ proposition is assumed to be false until proven otherwise, Tweety's birth state (capable of flight) is assumed to persist until the agent learns that Tweety's wing was broken.

Personally I find circumscription unsatisfying. To me, the most obvious answer for "How do you turn 'all' into 'most'?" is probability theory. As E. T. Jaynes showed, logic is merely a special case of probability theory (in which all of the probabilities are 0 or 1), so the jump from logic to probability theory seems more natural to me than circumscription. I am not alone in thinking this, of course. Many people attempted to solve the frame problem using probability theory, but as Pearl showed in 1988 regarding the Yale Shooting Problem, probability theory can never be enough, because it cannot describe counterfactuals, and thus cannot describe causality.

But that limitation disappeared in 1995, when Pearl figured out how to generalize probability theory. He discovered a complete set of axioms for his "calculus of causality", which distinguishes between observed conditional variables and intervened conditional variables.

    Logic -> Probability Theory -> Calculus of Causality (wow!)

According to the linked paper, the circumscriptive event calculus and Thielscher's fluent calculus have adequately solved the frame problem. But I still wonder, has anyone re-attempted a solution using the calculus of causality?﻿

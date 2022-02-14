#!/usr/bin/env python

import random

rgen = random.Random()

def start_game():
    name = raw_input("Greetings. What is your name? ")
    print "Hello, %s." % (name,)

    play_game()

def play_game():
    print "I am thinking of a number between 1 and 100."
    my_number = rgen.randint(1,100)
    num_guesses = 0
    while True:
        user_number = int(raw_input("Guess: "))
        num_guesses += 1
        if my_number == user_number:
            break
        elif my_number < user_number:
            print "Try lower."
        else:
            print "Try higher."

    print "Correct in %s guesses." % num_guesses
    play_again = raw_input("Play again? ")

    if play_again.startswith('y') or play_again.startswith('Y'):
        play_game()
    else:
        print "Thank you for playing."

if __name__=="__main__":
    start_game()

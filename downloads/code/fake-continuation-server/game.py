import random

rgen = random.Random()

class RandomNumberGame(object):
    def __init__(self, interface):
        self.interface = interface

    def start_game(self):
        name = self.interface.prompt_string(
                "Greetings. What is your name? ")
        self.interface.display("Hello, %s." % (name,))

        self.__play_game()

    def __play_game(self):
        self.interface.display("I am thinking of a number between 1 and 100.")
        my_number = self.interface.get(lambda: rgen.randint(1,100))
        num_guesses = 0
        while True:
            user_number = self.interface.prompt_int("Guess: ")
            num_guesses += 1
            if my_number == user_number:
                break
            elif my_number < user_number:
                self.interface.display("Try lower.")
            else:
                self.interface.display("Try higher.")

        self.interface.display("Correct in %s guesses." % num_guesses)
        play_again = self.interface.prompt_yes_no("Play again? ")

        if play_again:
            self.__play_game()
        else:
            self.interface.display("Thank you for playing.")

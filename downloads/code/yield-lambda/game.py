import random

rgen = random.Random()

class RandomNumberGame(object):
    def __init__(self, interface):
        self.interface = interface

    def __iter__(self):
        name = yield lambda: self.interface.prompt_string(
                "Greetings. What is your name? ")
        yield lambda: self.interface.display("Hello, %s." % (name,))

        # The coroutine equivalent of self.__play_game()
        iter = self.__play_game()
        try:
            y = yield iter.next()
            while True:
                y = yield iter.send(y)
        except StopIteration:
            pass

    def __play_game(self):
        yield lambda: self.interface.display("I am thinking of a number between 1 and 100.")
        my_number = yield lambda: rgen.randint(1,100)
        num_guesses = 0
        while True:
            user_number = yield lambda: self.interface.prompt_int("Guess: ")
            num_guesses += 1
            if my_number == user_number:
                break
            elif my_number < user_number:
                yield lambda: self.interface.display("Try lower.")
            else:
                yield lambda: self.interface.display("Try higher.")

        yield lambda: self.interface.display("Correct in %s guesses." % num_guesses)
        play_again = yield lambda: self.interface.prompt_yes_no("Play again? ")

        if play_again:
            # The coroutine equivalent of self.__play_game()
            iter = self.__play_game()
            try:
                y = yield iter.next()
                while True:
                    y = yield iter.send(y)
            except StopIteration:
                pass
        else:
            yield lambda: self.interface.display("Thank you for playing.")

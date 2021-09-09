#!/usr/bin/env python

class CommandLineInterface:
    def __init__(self, routine):
        self.routine = routine(self)

    def run(self):
        self.routine.start_game()

    def get(self, f):
        return f()

    def display(self, prompt):
        print prompt

    def prompt_string(self, prompt):
        return raw_input(prompt)

    def prompt_int(self, prompt):
        return int(raw_input(prompt))

    def prompt_yes_no(self, prompt):
        response = raw_input(prompt)
        return response.startswith('y') or response.startswith('Y')

if __name__=="__main__":
    from game import RandomNumberGame
    cmd = CommandLineInterface(RandomNumberGame)
    cmd.run()

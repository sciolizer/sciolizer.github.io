#!/usr/bin/env python

class CommandLineInterface(object):
    def __init__(self, routine):
        self.routine = routine(self)

    def run(self):
        iter = self.routine.__iter__()
        try:
            action = iter.next()
            while True:
                action = iter.send(action())
        except StopIteration:
            pass

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

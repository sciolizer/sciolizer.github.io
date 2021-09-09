#!/usr/bin/env python

import cgi
from wsgiref.simple_server import make_server

# Everytime we generate an html page, we create a hidden input element
# with this name. It lets us know which saved history must be resumed
# in order to continue the program.
HISTORY_FORM_NAME = 'WebInterface_history_index'

class History(object):
    """A record of past values returned by the routine. Useful for playback.
       self.get_pending is a function which takes a dictionary like object
           corresponding to the POST variables, and returns the new value
           to be added to the history.
       self.old_values is all of the results of functions yielded by the routine.
       """
    def __init__(self, get_pending, old_values):
        self.get_pending = get_pending
        self.old_values = old_values

class WebInterface(object):
    """WebInterface wraps around a routine class to allow for the routine to
       be executed through a browser. It works by remembering the results
       of functions that were yielded by the routine. In order to pick up
       where it left off, the routine is re-run with the remembered values,
       a new value is parsed from the POST variables, and the routine keeps
       running until it reaches another prompt."""
    def __init__(self, routine_class):
        self.routine_class = routine_class
        self.histories = [History(None, [])]

    def respond(self, environ, start_response):
        responder = WebInterface.Response(self, environ, start_response)
        return responder.respond()

    class Response(object):
        """The Response class is instantiated for every HTTP request.
           It grabs the appropriate history according to the value in the POST
           variable 'WebInterface_history_index'. Using that history, it
           re-runs the routine with the contained old_values, parses the POST
           variables for any new values using get_pending, and continues the
           routine until it needs to make another request. For simplicity,
           it modifies web_interface.histories directly. A real
           implementation would need to protect this variable using locks
           (or find a mutation-free solution), since it is possible for
           the wsgi server to make concurrent calls to WebInterface.respond.
           """
        def __init__(self, web_interface, environ, start_response): 
            self.web_interface = web_interface
            self.environ = environ
            self.start_response = start_response

        def respond(self):
            routine = self.web_interface.routine_class(self)
            self.form = cgi.FieldStorage(fp=self.environ['wsgi.input'],environ=self.environ)
            history_index = int(self.form.getvalue(HISTORY_FORM_NAME, default="0"))
            if len(self.web_interface.histories) <= history_index:
                self.start_response('412 Cannot read the future', [('Content-type', 'text/html')])
                return ["That history has not yet been written."]

            # Copy the history in order to create a new history.
            history_orig = self.web_interface.histories[history_index]
            self.history = History(history_orig.get_pending, history_orig.old_values[:])
            self.start_response('200 OK', [('Content-type', 'text/html')])
            self.output = [ '<form method="POST">\n' ]

            self.paused = False
            iter = routine.__iter__()
            try:
                # Re-run the routine over all old_values.
                action = iter.next()
                for history_value in self.history.old_values:
                    action = iter.send(history_value)

                # If a get_pending was previously set, invoke it in order
                # to parse the POST variables for any new values.
                if self.history.get_pending != None:
                    val = self.history.get_pending(self)
                    self.history.old_values.append(val)
                    action = iter.send(val)

                # Continue the routine until another prompt is made.
                while not self.paused:
                    new_value = action()
                    if not self.paused:
                        self.history.old_values.append(new_value)
                        action = iter.send(new_value)

            except StopIteration:
                pass

            self.web_interface.histories.append(self.history)
            self.output += '<input type="hidden" name="%s" value="%s">\n' % (HISTORY_FORM_NAME, len(self.web_interface.histories) - 1)
            self.output += '</form>\n'
            return self.output

        def display(self, str):
            self.output += str + "
\n"

        def prompt_string(self, prompt):
            self.prompt_type(prompt, str)

        def prompt_int(self, prompt):
            self.prompt_type(prompt, int)

        def prompt_yes_no(self, prompt):
            self.prompt_and_pause(
                    prompt,
                    [("submit", "btn_yes", "Yes"), ("submit", "btn_no", "No")],
                    lambda form: form.has_key('btn_yes'))

        def prompt_type(self, prompt, type_parse):
            self.prompt_and_pause(
                    prompt, 
                    [("text", "prompt", ""), ("submit", "btn_submit", "Enter")],
                    lambda form: type_parse(form["prompt"].value))

        def prompt_and_pause(self, prompt, inputs, parse_form):
            self.output += prompt
            for input in inputs:
                self.output += '<input type="%s" name="%s" value="%s">\n' % input
            self.paused = True
            def read_from_form(responder):
                return parse_form(responder.form)
            self.history.get_pending = read_from_form

if __name__=="__main__":
    from game import RandomNumberGame
    interface = WebInterface(RandomNumberGame)
    httpd = make_server('', 8000, interface.respond)
    httpd.serve_forever()

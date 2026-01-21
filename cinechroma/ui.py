""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""

# TODO: Implement terminal UI using Rich and pyfiglet

class DummyConsole:
    def print(self, msg):
        print(msg)

console = DummyConsole()

def show_banner():
    print("[banner] cinechroma CLI")
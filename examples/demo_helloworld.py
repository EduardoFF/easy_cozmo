"""
Makes cozmo saying "hello world"
"""

from easy_cozmo import *

def cozmo_program():
    say("Hello world")

run_program_with_viewer(cozmo_program)

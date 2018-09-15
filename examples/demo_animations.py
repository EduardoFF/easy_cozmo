"""
Makes cozmo saying "hello world"
"""

from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    set_volume_med()
    say("I am happy")
    show_happy()
    say("I am sad")
    show_sad()
    say("I am frustrated")
    show_frustrated()
    say("I am dancing")
    show_dancing()
    
    
run_program_with_viewer(cozmo_program)

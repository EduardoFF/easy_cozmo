from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps

"""
Task: Kick

last time tested:2019-09-23
"""

def cozmo_program():
    if scan_for_ball(360):
        if align_with_ball():
            kick()
            show_happy()
        else:
            say("I can't find the ball")
            show_sad()
    else:
        say("I can't find the ball")
        show_sad()

run_program_with_viewer(cozmo_program)

from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
def cozmo_program():
    i=0
    while i < 3:
        rotate_left(90)
        move_forward(20)
        rotate_left(90)
        move_forward(14)
        rotate_left(90)
        move_forward(20)
        rotate_left(90)
        move_forward(14)
        if i==0:
            say("First lap")
        elif i==1:
            say("Second lap")
        elif i==2:
            say("Third lap")
        i=i+1



run_program_with_viewer(cozmo_program)

from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
def cozmo_program():
    if scan_for_left_pole(360):
        if align_ball_and_left_pole():
            rotate_left(48.5)
            move_forward(6.6)
            rotate_right(90)
            say("Going to shoot")
            kick()
            say("Goal!")
            show_happy()
    else:
        if scan_for_right_pole(360):
            if align_ball_and_right_pole():
                rotate_right(48.5)
                move_forward(6.6)
                rotate_left(90)
                say("Going to shoot")
                kick()
                say("Goal!")
                show_happy()






run_program_with_viewer(cozmo_program)

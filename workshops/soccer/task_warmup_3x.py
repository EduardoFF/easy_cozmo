from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
def cozmo_program():
    cnt = 0
    while cnt < 3:
        move_forward(20)
        rotate_left(90)
        move_forward(14)
        rotate_left(90)
        move_forward(20)
        rotate_left(90)
        move_forward(14)
        rotate_left(90)
        cnt = cnt + 1

run_program_with_viewer(cozmo_program)

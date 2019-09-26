from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
def cozmo_program():
    rotate_left(90)
    move_forward(20)
    rotate_left(90)
    move_forward(14)
    rotate_left(90)
    move_forward(20)
    rotate_left(90)
    move_forward(14)

run_program_with_viewer(cozmo_program)

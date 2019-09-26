from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
def cozmo_program():
    from easy_cozmo.movements import _move_head
    easy_cozmo._robot.set_robot_volume(.1)
    init_ball_detection()
    _move_head(degrees(-11))
    move_lift_ground()
    if scan_for_ball(360):
        say("Ball found")



run_program_with_viewer(cozmo_program)

from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
from easy_cozmo.ball_detector import _align_ball_and_goal

""" Task: pass to closest player

steps:
1 - scan for cube 1, store distance in variable
2 - scan for cube 2, store distance in variable
3 - evaluate closest distance
4 - scan for ball
5 - align_ball_and_cube (selected cube)
6 - shoot
"""


def cozmo_program():
    from easy_cozmo.movements import _move_head
 #   easy_cozmo._robot.set_robot_volume(.6)
#    move_head_looking_down()
 #   pause(1)

    if scan_for_cube_by_id(360, 1):
        say("Found cube 1")
        d1 = distance_to_cube(1)
        if scan_for_cube_by_id(360, 2):
            say("Found cube 2")
            d2 = distance_to_cube(2)
            if d1 < d2:
                if align_ball_and_cube(1) and kick():
                    show_happy()
            else:
                if align_ball_and_cube(2) and kick():
                    show_happy()
        else:
            if align_ball_and_cube(1) and kick():
                show_happy()
            else:
                show_sad()
    else:
        if scan_for_cube_by_id(360, 2):
            say("Found cube 2")
            if align_ball_and_cube(1):
                kick()
                show_happy()
        else:
            say("Can't find any player")
            show_sad()







run_program_with_viewer(cozmo_program)

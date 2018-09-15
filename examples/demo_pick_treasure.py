"""
Pick the treasure using vision to steer the robot
"""

from mindcraft_treasure_hunt_cozmo import *

def pick_treasure():
    set_volume_high()
    move_head_looking_up()
    while(True):
        move_forward(4)
        if is_face_visible():
            align_with_face()
            say(" Thanks for guiding me!")
            if wait_for_a_smiling_face_visible(1):
                say(" I passed the gate, now I will look for the treasure!")
                move_head_looking_forward()
                if scan_for_cube_by_id(360, 1):
                    say("Picking up cube 1")
                    if pickup_cube_by_id(1):
                        break
                    else:
                        say("Problem picking up cube 1, I give up")
                        abort()
                else:
                    say("I can't find cube 1, I give up")
                    abort()
		 
    move_head_looking_up()
    move_lift_down()
    while(True):
        move_forward(4)
        if is_face_visible():
            align_with_face()
            say(" Thanks for guiding me!")
            if wait_for_a_smiling_face_visible(1):
                say("Back home!")
                drop_cube()
                say("Enjoy the treasure")

    
run_program_with_viewer(pick_treasure)

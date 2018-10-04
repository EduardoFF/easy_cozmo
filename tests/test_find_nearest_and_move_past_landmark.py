from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    move_head_looking_forward()
    if scan_for_landmark(360):
        say("Found landmark")
        if align_with_nearest_landmark():
            say("aligned success")
        else:
            say("aligned failed, abort")
            abort()
        move_forward_avoiding_landmarks(20)
    else:
        say("I can't find a landmark")
        
run_program_with_viewer(cozmo_program)

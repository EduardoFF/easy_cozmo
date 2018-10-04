from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    while(True):
        if scan_for_landmark(360):
            say("Found landmark")
            if align_with_nearest_landmark():
                say("aligned success")
            else:
                say("aligned failed")
        else:
            say("I can't find a landmark")
        
run_program_with_viewer(cozmo_program)

from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    move_head_looking_up()
    while True:
        if scan_for_faces(360):
            say("I see a face")
            align_with_face()
        else:
            say("I can't find a face, trying again")
            pause(1)
            
        
run_program_with_viewer(cozmo_program)

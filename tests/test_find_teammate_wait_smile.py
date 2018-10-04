from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    set_volume_low()
    move_head_looking_up()
    while True:
        if scan_for_teammates(360):
            say("I see a teammate")
            align_with_face()
            say_something_to_visible_teammate("Hello", ", smile")
            if wait_for_a_smiling_face_visible(5):
                say("yes")
            else:
                say("no")
        else:
            say("I can't find a teammate, trying again")
            pause(1)
            
        
run_program_with_viewer(cozmo_program)

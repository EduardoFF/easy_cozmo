from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    if align_with_nearest_cube():
        say_text("Aligned success")
    else:
        say_text("Aligned failed")
        
run_on_cozmo_debug_mode(cozmo_program)

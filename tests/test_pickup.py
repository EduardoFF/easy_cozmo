from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    for i in range(1,4):
        if pickup_cube_by_id(i):
            say_text("Cube ", i, " picked up")
            drop_cube()
        else:
            say_text("Cube ", i, " not picked up")
        pause(3)
    
        
run_on_cozmo_debug_mode(cozmo_program)

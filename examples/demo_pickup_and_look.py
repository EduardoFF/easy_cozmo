"""
Exercise 1
"""
from mindcraft_treasure_hunt_cozmo import *

def pickup_cubes():
    for cube_id in [1,2,3]:
        say("Searching for cube", cube_id)
        move_head_looking_forward()
        if scan_for_cube_by_id(360, cube_id):
            say("Picking up cube", cube_id)
        if pickup_cube_by_id(cube_id):
            move_lift_down()
            move_head_looking_up()
            say("Searching for a teammate")
            if scan_for_teammates():
                say_something_to_visible_teammate( "Look, ", " this is cube ", cube_id)
            drop_cube()
        
run_program_with_viewer(pickup_cubes)

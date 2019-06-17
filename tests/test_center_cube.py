from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(0)
    cube_id = 2
    if scan_for_cube_by_id(360,cube_id):
        if center_cube(cube_id):
            say("OK")
        else:
            say("Can't center cube")
    else:
        say("Can't find cube")

run_program_with_viewer(cozmo_program)

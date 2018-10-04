"""
Picks up cube one and places it on cube two
"""
from mindcraft_treasure_hunt_cozmo import *
def pickup_and_place():
    say("Searching for cube one")
    move_head_looking_forward()
    completed = False
    if scan_for_cube_one(360):
        say("Picking up cube one")
        if pickup_cube_one():
            move_lift_up()
            move_head_looking_forward()
            say("Searching for cube two")
            if scan_for_cube_two(360):
                say("Placing cube one on top of cube two")
                if place_on_top(2):
                    completed = True    
                else:
                    say("Sorry, I couldn't place the cube")
            else:
                say("I couldn't find the cube")
        else:
            say("Sorry, I couldn't pick the cube")
    else:
        say("Sorry, I couldn't find the cube")
    if completed:
        say("Completed the task")
        show_dancing()
    else:
        say("Failed the task")
        show_sad()

run_program_with_viewer(pickup_and_place)
#run_program(pickup_cubes)

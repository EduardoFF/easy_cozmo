#!/usr/bin/env python3

'''

'''

from mindcraft_treasure_hunt_cozmo import *

def cozmo_program_noloop():
    say_text("Searching cube one")
    move_head_straight()
    if scan_for_cube_one(360):
        say_text("Picking up cube one")
        if pickup_cube_one():
            move_lift_down()
            move_head_up()
            say_text("Searching any teammate")
            if scan_for_any_teammate():
                say_something_to_visible_teammate( "Look ", ", this is cube one")

            drop_cube()
        
    
    move_head_straight()
    say_text("Searching cube two")
    if scan_for_cube_two(360):
        say_text("Picking up cube two")
        if pickup_cube_two():
            move_lift_down()
            move_head_up()
            say_text("Searching any teammate")
            if scan_for_any_teammate():
                say_something_to_visible_teammate( "Look ", ", this is cube two")

            drop_cube()

    move_head_straight()
    say_text("Searching cube three")
    if scan_for_cube_three(360):
        say_text("Picking up cube three")
        if pickup_cube_three():
            move_lift_down()
            move_head_up()
            say_text("Searching any teammate")
            if scan_for_any_teammate():
                say_something_to_visible_teammate( "Look ", ", this is cube three")

            drop_cube()

def cozmo_program_loop():
    for cube_id in range(1,4):
        say_text("Searching cube", cube_id)
        move_head_straight()
        if scan_for_cube_by_id(360, cube_id):
            say_text("Picking up cube", cube_id)
        if pickup_cube_by_id(cube_id):
            move_lift_down()
            move_head_up()
            say_text("Searching any teammate")
            if scan_for_any_teammate():
                say_something_to_visible_teammate( "Look ", ", this is cube ", cube_id)
            drop_cube()
        
#run_on_cozmo_with_viewer(cozmo_program_noloop)
run_on_cozmo_with_viewer(cozmo_program_loop)

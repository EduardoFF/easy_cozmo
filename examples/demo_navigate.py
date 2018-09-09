#!/usr/bin/env python3

from mindcraft_treasure_hunt_cozmo import *


def my_search_strategy():
    move_head_straight()
    if double_scan_for_any_cube(30):
        return True
    rotate_in_place(90)
    if double_scan_for_any_cube(30):
        return True
    rotate_in_place(-180)
    if double_scan_for_any_cube(30):
        return True
    return False
    

def cozmo_program():
    while(True):
        say_text("Searching any cube")
        if not my_search_strategy():
            say_text("Can't find cube, trying again")
            continue
        if not align_with_nearest_cube():
            say_text("Can't align, trying again")
        move_forward_avoiding_cubes(250)
        
        
        
        
run_on_cozmo_with_viewer(cozmo_program)

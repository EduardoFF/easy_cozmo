#!/usr/bin/env python3

from mindcraft_treasure_hunt_cozmo import *


def my_search_strategy():
    move_head_straight()
    if double_scan_for_object(30):
        return True
    rotate_in_place(90)
    if double_scan_for_object(30):
        return True
    rotate_in_place(-180)
    if double_scan_for_object(30):
        return True
    return False
    

def cozmo_program():
    while(True):
        pause(.5)
        continue
#        say_text("Searching for object")

        if not my_search_strategy():
            say_text("Can't find object, trying again")
            continue
        if not align_with_nearest_object(distance=150):
            say_text("Can't align, trying again")
        move_forward_avoiding_obstacles(300)
        
        
        
        
run_on_cozmo_debug_mode(cozmo_program)

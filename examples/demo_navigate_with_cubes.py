#!/usr/bin/env python3

from mindcraft_treasure_hunt_cozmo import *


def find_next_landmark():
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
    

def navigation_with_landmarks():
    while(True):
        say("Searching for the next landmark")
        if find_next_landmark():
            if align_with_nearest_landmark():
                move_forward_avoiding_landmarks(250)
            else:
                say("Can't align, trying again")
        else:
            say("Can't find landmark, trying again")            
        
        
        
        
run_on_cozmo_debug_mode(cozmo_program)

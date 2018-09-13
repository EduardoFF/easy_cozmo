from mindcraft_treasure_hunt_cozmo import *


def find_next_landmark():
    move_head_looking_forward()
    if scan_for_landmark(30):
        return True
    if scan_for_landmark(-60):
        return True
    rotate_in_place(120)
    if scan_for_landmark(30):
        return True
    if scan_for_landmark(-60):
        return True
    rotate_in_place(-120)
    if scan_for_landmark(30):
        return True
    if scan_for_landmark(-60):
        return True

    return False
    

def navigation_with_landmarks():
    set_volume_low()
    landmarks = 0
    total_landmarks = 9
    while(True):
        say("Searching for the next landmark")
        if find_next_landmark():
            if align_with_nearest_landmark():
                move_forward_avoiding_landmark(25)
                landmarks = landmarks + 1
            else:
                say("Can't align with the landmark, trying again")
                continue
        else:
            say("Can't find a landmark, trying again")
            continue
        if landmarks == total_landmarks:
            say("Navigation job done!")
            break
        
run_program_with_viewer(navigation_with_landmarks)

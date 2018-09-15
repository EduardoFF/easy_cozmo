from mindcraft_treasure_hunt_cozmo import *


def find_next_landmark():
    move_head_looking_forward()
    move_lift_down()
    if scan_for_landmark(90):
        return True
    if scan_for_landmark(-180):
        return True
    if scan_for_landmark(180):
        return True

    return False
    

def navigation_with_landmarks():
    set_volume_med()
    #enable_camera_settings_for_bright_light()
        
    landmarks = 0
    total_landmarks = 9
    while(True):
        say("Searching for the next landmark")
        if find_next_landmark():
            if align_with_nearest_landmark():
                move_forward_avoiding_landmark(30)
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

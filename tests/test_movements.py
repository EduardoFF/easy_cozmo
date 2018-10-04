from mindcraft_treasure_hunt_cozmo import *
from mindcraft_treasure_hunt_cozmo.say import _say
def cozmo_program():

    
    set_volume_low()
    _say("moving forward 10 cm")
    move_forward(10)
    _say("rotate in place 90 degrees")
    rotate_in_place(90)
    _say("rotate in place -90 degrees")
    rotate_in_place(-90)
    _say("rotate in place 540  degrees")
    rotate_in_place(540)
    _say("rotate in place -180 degrees")
    rotate_in_place(-180)
    
    _say("reverse 10cm")
    reverse(10)
    _say("lift up")
    move_lift_up()
    _say("lift down")
    move_lift_down()
    _say("lift up")
    move_lift_up()
    _say("lift ground")
    move_lift_ground()
    _say("head up")
    move_head_looking_up()
    _say("head down")
    move_head_looking_down()
    _say("head forward")
    move_head_looking_forward()
    
        
run_program_with_viewer(cozmo_program)

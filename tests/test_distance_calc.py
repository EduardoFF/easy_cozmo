""" Test estimation of distance traveled using odometry """
from mindcraft_treasure_hunt_cozmo import *

def cozmo_program():
    set_volume_low()
    initialize_odometry()
    def move_50cm():
        for i in range(5):
            move_forward(10)
            print("Distance traveled ", get_distance_traveled())
            pause(1)
    move_50cm()
    rotate(90)
    move_50cm()
    rotate(90)
    move_50cm()
    rotate(90)
    move_50cm()    
    
        
    
    
        
run_program_with_viewer(cozmo_program)

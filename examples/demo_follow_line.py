from mindcraft_treasure_hunt_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    move_lift_ground()
    while True:
        angle = get_detected_line_angle()
        if angle:
            print("angle: ", angle)
            if angle < -15:
                # should move left
                if angle >-30 :
                    right_speed = 2
                    left_speed = 4
                elif angle < -30:
                    right_speed = 0
                    left_speed = 5
                else:
                    right_speed = -2
                    left_speed = 2
            elif angle > 15:
                #should move right
                if angle < 30 :
                    right_speed = 4
                    left_speed = 2
                else:
                    right_speed = 5
                    left_speed =0
            else:
                left_speed = 5
                right_speed = 5
            set_wheels_speeds(left_speed, right_speed)
        else:
            stop()
        pause(0.05)

        
run_program_with_viewer(cozmo_program)

from mindcraft_treasure_hunt_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    init_line_detection()
    move_lift_ground()
    while True:
        if not is_line_detected():
            stop()
        else:
            move()
            angle = get_detected_line_angle()            
            if angle <= -30:
                steer(-100)
            elif -30 < angle < -15:
                steer(-50)
            elif -15 <= angle <= 15:
                steer(0)
            elif 15 < angle <= 30:
                steer(50)
            elif 30 < angle:
                steer(100)

        
run_program_with_viewer(cozmo_program)

from mindcraft_treasure_hunt_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
def cozmo_program():
    from mindcraft_treasure_hunt_cozmo.movements import _move_head
    mindcraft._mycozmo.set_robot_volume(.1)
    _move_head(degrees(-11))
    move_lift_ground()
    linedetect = LineDetector(mindcraft._mycozmo)
    while True:
        pause(1)
            
        
run_program_with_viewer(cozmo_program)

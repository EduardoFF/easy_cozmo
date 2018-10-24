from mindcraft_treasure_hunt_cozmo import *
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    
    mindcraft._mycozmo.world.define_custom_wall(CustomObjectTypes.CustomType05,
                                                CustomObjectMarkers.Circles3,
                                                180, 180, 180, 180, True)

    landmarks = {CustomObjectTypes.CustomType05: Pose(0,0,0, angle_z = degrees(0))}
    initialize_landmark_localization()
    pause(3)
    while True:
       # where_am_i()
        print(get_odom_pose())
        pause(0.5)
        
run_program_with_viewer(cozmo_program)

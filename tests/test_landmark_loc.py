from mindcraft_treasure_hunt_cozmo import *
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians

def cozmo_program():
    mindcraft._mycozmo.set_robot_volume(.1)
    
    mindcraft._mycozmo.world.define_custom_wall(CustomObjectTypes.CustomType05,
                                                CustomObjectMarkers.Circles3,
                                                180, 180, 180, 180, True)

    landmarks = {CustomObjectTypes.CustomType05: Pose(0,0,0, angle_z = degrees(0))}
    initialize_landmark_localization(landmarks)
    pause(3)
    where_am_i()
        
run_program_with_viewer(cozmo_program)

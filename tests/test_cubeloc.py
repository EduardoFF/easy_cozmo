from easy_cozmo import *
import easy_cozmo.easy_cozmo as mc
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
from easy_cozmo.cube_localization import *
def cozmo_program():
    mc._robot.set_robot_volume(.1)

    mc._robot.world.define_custom_wall(CustomObjectTypes.CustomType05,
                                                CustomObjectMarkers.Circles3,
                                                180, 180, 180, 180, True)

    initialize_cube_localization()
    pause(3)
    while True:
       # where_am_i()
        print(get_odom_pose())
        pause(0.5)

run_program_with_viewer(cozmo_program)

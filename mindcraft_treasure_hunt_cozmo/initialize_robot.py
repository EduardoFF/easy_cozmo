from .mindcraft_defaults import df_volume, df_image_stream_enabled
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
import time
from .movements import move_lift_down
from .robot_utils import enable_head_light, disable_head_light
from .mindcraft_defaults import *
def initialize_robot(robot):
    robot.enable_all_reaction_triggers(False)
    # define custom objects
    unique_marker = False
    robot.world.undefine_all_custom_marker_objects()
    time.sleep(1)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType01,
                                   CustomObjectMarkers.Circles2,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType02,
                                   CustomObjectMarkers.Diamonds2,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType03,
                                   CustomObjectMarkers.Hexagons2,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType04,
                                   CustomObjectMarkers.Triangles2,
                                   65, 65, 40, 40, unique_marker)
    
    robot.world.define_custom_wall(CustomObjectTypes.CustomType05,
                                   CustomObjectMarkers.Circles3,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType06,
                                   CustomObjectMarkers.Diamonds3,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType07,
                                   CustomObjectMarkers.Hexagons3,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType08,
                                   CustomObjectMarkers.Triangles3,
                                   65, 65, 40, 40, unique_marker)
    
    robot.world.define_custom_wall(CustomObjectTypes.CustomType09,
                                   CustomObjectMarkers.Circles4,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType10,
                                   CustomObjectMarkers.Diamonds4,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType11,
                                   CustomObjectMarkers.Hexagons4,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType12,
                                   CustomObjectMarkers.Triangles4,
                                   65, 65, 40, 40, unique_marker)

    robot.world.define_custom_wall(CustomObjectTypes.CustomType13,
                                   CustomObjectMarkers.Circles5,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType14,
                                   CustomObjectMarkers.Diamonds5,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType15,
                                   CustomObjectMarkers.Hexagons5,
                                   65, 65, 40, 40, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType16,
                                   CustomObjectMarkers.Triangles5,
                                   65, 65, 40, 40, unique_marker)

                                   
                                   
    # todo: disable it by default
#    robot.enable_facial_expression_estimation(False)
    robot.set_robot_volume(df_volume)
    move_lift_down()
    disable_head_light()
    if df_camera_auto_exposure_enabled:
        robot.camera.enable_auto_exposure(True)
    else:
        exposure_range = robot.camera.config.max_exposure_time_ms - robot.camera.config.min_exposure_time_ms
        exposure = robot.camera.config.min_exposure_time_ms + int(exposure_range*0.1)

        gain_range = robot.camera.config.max_gain -  robot.camera.config.min_gain
        gain =  robot.camera.config.min_gain + gain_range*0.1
    #robot.camera.set_manual_exposure(exposure, gain)
    
    robot.camera.image_stream_enabled = True
    #print("camera.image_stream_enabled ", df_image_stream_enabled)
    robot.world.disconnect_from_cubes()

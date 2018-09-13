from .mindcraft_defaults import df_volume, df_image_stream_enabled
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes

def initialize_robot(robot):
    robot.enable_all_reaction_triggers(False)
    # define custom objects
    unique_marker = False
    robot.world.define_custom_wall(CustomObjectTypes.CustomType01,
                                   CustomObjectMarkers.Circles2,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType02,
                                   CustomObjectMarkers.Diamonds2,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType03,
                                   CustomObjectMarkers.Hexagons2,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType04,
                                   CustomObjectMarkers.Triangles2,
                                   100, 60, 50, 50, unique_marker)
    
    robot.world.define_custom_wall(CustomObjectTypes.CustomType05,
                                   CustomObjectMarkers.Circles3,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType06,
                                   CustomObjectMarkers.Diamonds3,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType07,
                                   CustomObjectMarkers.Hexagons3,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType08,
                                   CustomObjectMarkers.Triangles3,
                                   100, 60, 50, 50, unique_marker)
    
    robot.world.define_custom_wall(CustomObjectTypes.CustomType09,
                                   CustomObjectMarkers.Circles4,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType10,
                                   CustomObjectMarkers.Diamonds4,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType11,
                                   CustomObjectMarkers.Hexagons4,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType12,
                                   CustomObjectMarkers.Triangles4,
                                   100, 60, 50, 50, unique_marker)

    robot.world.define_custom_wall(CustomObjectTypes.CustomType13,
                                   CustomObjectMarkers.Circles5,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType14,
                                   CustomObjectMarkers.Diamonds5,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType15,
                                   CustomObjectMarkers.Hexagons5,
                                   100, 60, 50, 50, unique_marker)
    robot.world.define_custom_wall(CustomObjectTypes.CustomType16,
                                   CustomObjectMarkers.Triangles5,
                                   100, 60, 50, 50, unique_marker)

                                   
                                   
    # todo: disable it by default
#    robot.enable_facial_expression_estimation(False)
    robot.set_robot_volume(df_volume)
    robot.camera.enable_auto_exposure(True)
    exposure_range = robot.camera.config.max_exposure_time_ms - robot.camera.config.min_exposure_time_ms
    exposure = robot.camera.config.min_exposure_time_ms + int(exposure_range*0.25)

    gain_range = robot.camera.config.max_gain -  robot.camera.config.min_gain
    gain =  robot.camera.config.min_gain + gain_range*0.1
#    robot.camera.set_manual_exposure(exposure, gain)
    
    robot.camera.image_stream_enabled = True
    print("camera.image_stream_enabled ", df_image_stream_enabled)
    robot.set_lift_height(0).wait_for_completed()
    robot.world.disconnect_from_cubes()

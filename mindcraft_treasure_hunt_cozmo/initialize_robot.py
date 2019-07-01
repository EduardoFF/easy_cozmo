from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
import time
from .movements import move_lift_down
from .robot_utils import enable_head_light, disable_head_light
from .defaults import *
from .line_detector import initialize_line_detector
def initialize_robot(robot):
    robot.enable_all_reaction_triggers(False)
    robot.world.undefine_all_custom_marker_objects()
    time.sleep(1)

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
    if df_enable_line_detection:
        initialize_line_detector('hough')

    #print("camera.image_stream_enabled ", df_image_stream_enabled)
    robot.world.disconnect_from_cubes()

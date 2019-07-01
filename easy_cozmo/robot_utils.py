import time
from . import easy_cozmo


def enable_camera_settings_for_bright_light():
    robot = easy_cozmo._robot
    robot.camera.enable_auto_exposure(False)
    exposure_range = robot.camera.config.max_exposure_time_ms - robot.camera.config.min_exposure_time_ms
    exposure = robot.camera.config.min_exposure_time_ms + int(exposure_range*0.05)

    gain_range = robot.camera.config.max_gain -  robot.camera.config.min_gain
    gain =  robot.camera.config.min_gain + gain_range*0.1
    robot.camera.set_manual_exposure(exposure, gain)

def disable_camera_settings_for_bright_light():
    robot = easy_cozmo._robot
    robot.camera.enable_auto_exposure(True)


def pause(time_in_seconds):
    """**Pause for certain amount of time in seconds**

    :param time_in_seconds: time to pause
    :type time_in_seconds: float
    """
    time.sleep(time_in_seconds)

def abort():
    """**Abort the entire program execution**
    """
    print("Aborting program...")
    raise SystemExit

def set_volume_high():
    easy_cozmo._robot.set_robot_volume(1)
def set_volume_low():
    easy_cozmo._robot.set_robot_volume(.05)
def set_volume_med():
    easy_cozmo._robot.set_robot_volume(.5)


def enable_head_light():
    """**Enable head light to see in low light conditions**
    """

    easy_cozmo._robot.set_head_light(True)
def disable_head_light():
    """**Disable head light**
    """

    easy_cozmo._robot.set_head_light(False)

#import mindcraft
#from mindcraft_defaults import _df_reverse_speed, _df_rotate_speed
from cozmo.util import degrees, Pose
import cozmo
from . import mindcraft

from .mindcraft_defaults import  _df_reverse_speed, \
    _df_rotate_speed

def rotate_in_place(angle):
    try:
        mindcraft._mycozmo.turn_in_place(degrees(angle),speed=_df_rotate_speed).wait_for_completed()
    except:
        say_error("Can't rotate, sorry")
        return False
    return True


def move_head_up():
    action=None
    try:
        action=mindcraft._mycozmo.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE)
        action.wait_for_completed()
        if action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Move head failed: code=%s reason='%s' result=%s" % (code, reason, result))
            mindcraft.say_error("Couldn't move head, sorry")
            action.abort()
            return False
        else:
            return True
    except:
        mindcraft.say_error("Couldn't move head, sorry")
    return False

def move_head_straight():
    action=None
    try:
        action=mindcraft._mycozmo.set_head_angle(degrees(0))
        action.wait_for_completed()
        if action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Move head failed: code=%s reason='%s' result=%s" % (code, reason, result))
            mindcraft.say_error("Couldn't pickup, sorry")
            action.stop()
            return False
        else:
            return True
    except:
        mindcraft.say_error("Couldn't pickup, sorry")
    return False
    
def move_lift_down():
    mindcraft._mycozmo.set_lift_height(0.2).wait_for_completed()

def move_lift_ground():
    mindcraft._mycozmo.set_lift_height(0).wait_for_completed()

def reverse_in_seconds(duration):
    mindcraft._mycozmo.drive_wheels(_df_reverse_speed, _df_reverse_speed, duration=2)

def move_forward_avoiding_cubes(distance):
    pose = Pose(distance, 0, 0, angle_z=degrees(0))
    mindcraft._mycozmo.go_to_pose(pose, relative_to_robot=True).wait_for_completed()


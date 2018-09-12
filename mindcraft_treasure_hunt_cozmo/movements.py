#import mindcraft
#from mindcraft_defaults import _df_reverse_speed, _df_rotate_speed
from cozmo.util import degrees, Pose
import cozmo
from . import mindcraft
from .say import _say_error, say_error
from .mindcraft_defaults import  _df_reverse_speed, \
    _df_rotate_speed

def rotate_in_place(angle):
     """**Rotate in place for a given angle**
    
    :param angle: Rotation angle (in degrees) 
    :type angle: float

    :return: True (suceeded) or False (failed)
    """
     try:
         mindcraft._mycozmo.turn_in_place(degrees(-1*angle),speed=_df_rotate_speed).wait_for_completed()
     except Exception as e:
         import traceback
         print(e)
         traceback.print_exc()
         say_error("I can't rotate, sorry")
         return False
     return True


def move_head_up():
    """**Move head in looking up position**

    :return: True (suceeded) or False (failed)
    """
    action=None
    try:
        action=mindcraft._mycozmo.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE)
        action.wait_for_completed()
        if action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Move head failed: code=%s reason='%s' result=%s" % (code, reason, result))
            say_error("I couldn't move my head, sorry")
            try:
                if action.is_running:
                    action.abort()
                    while action.is_running:
                        action.abort()
                        time.sleep(0.5)
            except Exception as e:
                import traceback
                print(e)
                traceback.print_exc()
                say_error("Move head faulty")
            return False
        else:
            return True
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Couldn't move head, sorry")
    return False

def move_head_straight():
    """**Move head in looking forward (at ground level) position**

    :return: True (suceeded) or False (failed)
    """
    action=None
    try:
        action=mindcraft._mycozmo.set_head_angle(degrees(0))
        action.wait_for_completed()
        if action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Move head failed: code=%s reason='%s' result=%s" % (code, reason, result))
            _say_error("I couldn't move my head, sorry")
            return False
        else:
            return True
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("I couldn't move my head , sorry")
    return False
    
def move_lift_down():
    """**Move lift close to the ground level**

    :return: True (suceeded) or False (failed)
    """
    action = mindcraft._mycozmo.set_lift_height(0.2)
    retval = True
    try:
        action.wait_for_completed()
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("I can't move my lift")
        retval=False
    try:
        while action.is_running:
            action.abort()
            time.sleep(.5)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Scan faulty")
        retval=False
    return retval

def move_lift_ground():
    """**Move lift to lowest (ground-level) position**

    :return: True (suceeded) or False (failed)
    """

    action = mindcraft._mycozmo.set_lift_height(0)
    retval = True
    try:
        action.wait_for_completed()
    except:
        say_error("I can't move my lift")
        retval=False
    try:
        while action.is_running:
            action.abort()
            time.sleep(0.5)
    except:
        say_error("Lift faulty")
        retval=False
    return retval
    

def reverse_in_seconds(duration):
    """**Reverse for certain amount of time in seconds**
    :param duration: Amount of time in seconds to apply reverse
    :type duration: float

    :return: True (suceeded) or False (failed)
    """
    try:
        mindcraft._mycozmo.drive_wheels(_df_reverse_speed, _df_reverse_speed, duration=2)
    except Exception as e:
        say_error("I can't move in reverse")
        return False
    return True

def move_forward_avoiding_obstacles(distance):
    """**Move forward for a given distance while avoiding cubes and
    visible objects on the way**

    :param duration: Distance in millimeters
    :type duration: float

    :return: True (suceeded) or False (failed)
    """
    pose = Pose(distance, 0, 0, angle_z=degrees(0))
    action = mindcraft._mycozmo.go_to_pose(pose, relative_to_robot=True)
    try:
        action.wait_for_completed()
        if action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Move forward failed: code=%s reason='%s' result=%s" % (code, reason, result))
            say_error("Couldn't move forward, sorry")
            return False
        else:
            return True
    except Exception as e:
        say_error("Move forward faulty, aborting")
        try:
            while action.is_running:
                action.abort()
                time.sleep(.5)
        except:
            pass
        return False
    return False




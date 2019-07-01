from cozmo.util import degrees, Pose, distance_mm, speed_mmps
import cozmo
from . import easy_cozmo
from .say import _say_error, say_error
from .defaults import  df_reverse_speed, \
    df_rotate_speed, df_forward_speed, df_max_wheel_speed

def rotate_in_place(angle):
    """**Rotate in place for a given angle in degrees**

    :param angle: Rotation angle (in degrees)
    :type angle: float

    :return: True (succeeded) or False (failed)
    """
    action = easy_cozmo._robot.turn_in_place(degrees(-1*angle),speed=degrees(df_rotate_speed))
    try:
        action.wait_for_completed()
        if action.has_succeeded:
            return True
        else:
            code, reason = action.failure_reason
            result = action.result
            print("WARNING RotateInPlace: code=%s reason='%s' result=%s" % (code, reason, result))
            say_error("I couldn't rotate, sorry")
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("I can't rotate, sorry")
    try:
        while action.is_running:
            action.abort()
            time.sleep(.5)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Wheels faulty")

    return False

def rotate(angle):
    return rotate_in_place(angle)

def rotate_right(angle):
    return rotate_in_place(angle)

def rotate_left(angle):
    return rotate_in_place(-1*angle)

def _move_head(angle):
    action=None
    try:
        action=easy_cozmo._robot.set_head_angle(angle)
        action.wait_for_completed()
        if action.has_succeeded:
            return True
        else:
            code, reason = action.failure_reason
            result = action.result
            print("WARNING: Move head: code=%s reason='%s' result=%s" % (code, reason, result))
            say_error("I couldn't move my head, sorry")
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("I couldn't move my head, sorry")
    try:
        while action.is_running:
            action.abort()
            time.sleep(0.5)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Move head faulty")

    return False


def move_head_looking_up():
    """**Move head in looking up position**

    :return: True (suceeded) or False (failed)
    """
    return _move_head(cozmo.robot.MAX_HEAD_ANGLE)

def move_head_looking_down():
    """**Move head in looking down position**

    :return: True (succeededed) or False (failed)
    """
    return _move_head(cozmo.robot.MIN_HEAD_ANGLE)

def move_head_looking_forward():
    """**Position head in looking forward (at ground level) position**

    :return: True (succeededed) or False (failed)
    """
    return _move_head(degrees(0))

def _move_lift(height):
    action = easy_cozmo._robot.set_lift_height(height)
    try:
        action.wait_for_completed()
        if action.has_succeeded:
            return True
        else:
            code, reason = action.failure_reason
            result = action.result
            print("WARNING: Move head: code=%s reason='%s' result=%s" % (code, reason, result))
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("I can't move my lift")
    try:
        while action.is_running:
            action.abort()
            time.sleep(.5)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Scan faulty")
    return False

def move_lift_down():
    """**Move lift close to the ground level**

    :return: True (succeededed) or False (failed)
    """
    return _move_lift(0.2)

def move_lift_ground():
    """**Move lift to lowest (ground-level) position**

    :return: True (succeededed) or False (failed)
    """
    return _move_lift(0)

def move_lift_up():
    """**Move lift close to the highest position**

    :return: True (succeededed) or False (failed)
    """
    return _move_lift(1)

def reverse_in_seconds(duration):
    """**Reverse for certain amount of time in seconds**
    :param duration: Amount of time in seconds to apply reverse
    :type duration: float

    :return: True (succeededed) or False (failed)
    """
    try:
        easy_cozmo._robot.drive_wheels(-1*df_reverse_speed, -1*df_reverse_speed, duration=duration)
    except Exception as e:
        say_error("I can't move in reverse")
        return False
    return True

def reverse(distance):
    duration = 10.0 * distance / df_reverse_speed
    #print("reversing for ",duration, "seconds")
    return reverse_in_seconds(duration)

def move_backward(distance):
    return reverse(distance)

def move():
    if easy_cozmo._robot.are_wheels_moving:
        return True
    fspeed = int(df_forward_speed / 10)
    return set_wheels_speeds(fspeed,fspeed)


def move_forward(distance=None):
    if distance is None:
        return move()
    action =  easy_cozmo._robot.drive_straight(distance_mm(distance*10),
                                                speed=speed_mmps(df_forward_speed),
                                                should_play_anim=False)
    try:
        action.wait_for_completed()
        if action.has_succeeded:
            return True
        else:
            code, reason = action.failure_reason
            result = action.result
            print("WARNING: Move forward: code=%s reason='%s' result=%s" % (code, reason, result))

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("I can't move forward")
    try:
        while action.is_running:
            action.abort()
            time.sleep(.5)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Wheels faulty")

    return False

def move_forward_in_seconds(distance):
    pass

def _execute_go_to_pose(pose, relative=True):

    action = easy_cozmo._robot.go_to_pose(pose, relative_to_robot=relative,
                                           num_retries=3)
    try:
        action.wait_for_completed()
        if action.has_succeeded:
            return True
        else:
            code, reason = action.failure_reason
            result = action.result
            print("WARNING GoToPose: code=%s reason='%s' result=%s" % (code, reason, result))
            _say_error("difficulties moving forward, sorry")
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Move forward faulty, aborting")
    try:
        while action.is_running:
            action.abort()
            time.sleep(.5)
    except:
        import traceback
        print(e)
        traceback.print_exc()
        say_error("Move forward faulty, aborting")

    return False


def move_forward_avoiding_landmark(distance):
    """**Move forward for a given distance while avoiding landmarks on
    the way**

    :param duration: Distance in centimeters
    :type duration: float

    :return: True (succeeded) or False (failed)
    """
    distance = distance * 10
    pose = Pose(distance, 0, 0, angle_z=degrees(0))
    return _execute_go_to_pose(pose)


def set_wheels_speeds(left_speed, right_speed):
    """ Set the wheels speeds in cm """
    left_speed *= 10
    right_speed *= 10
    if abs(left_speed) > df_max_wheel_speed \
       or abs(right_speed) > df_max_wheel_speed:
        say_error("Invalid speed")
        return False

    easy_cozmo._robot.drive_wheel_motors(int(left_speed), int(right_speed),\
                                          l_wheel_acc=200, r_wheel_acc=200)
    return True
def stop():
    if not easy_cozmo._robot.are_wheels_moving:
        return True
    easy_cozmo._robot.stop_all_motors()
    return True

def stop_moving():
    return stop()

def drive():
    return move()

def start_moving():
    return move()

def steer(value):
    w = 45
    v = 50
    if value == 0:
        return set_wheels_speeds(5,5)
    swap = False
    if value < 0:
        swap = True
        value *= -1
    # normalize
    if value > 100:
        value = 1
    value = int(((100 - value)/100.)*(600-50) + 50)

    rl = value
    rr = value + 45
    vl = (100*rl)/(rr+rl)
    vr = 100 - vl
    if swap:
        vl, vr = vr, vl
    return set_wheels_speeds(vl/10., vr/10.)

def steer_left(value):
    if value < 0:
        say_error("Invalid negative steer value")
        return False
    return steer(-1*value)

def steer_right(value):
    if value < 0:
        say_error("Invalid negative steer value")
        return False
    return steer(value)

def steer_straight():
    return steer(0)

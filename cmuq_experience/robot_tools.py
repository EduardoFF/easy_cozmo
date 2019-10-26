from mygotopose import MyGoToPose
import easy_cozmo.easy_cozmo as mc
from easy_cozmo.robot_utils import enable_head_light, pause
from easy_cozmo.say import say, say_error
from cozmo.util import degrees, Angle, Pose, distance_mm, radians, rotation_z_angle
from easy_cozmo.cube_localization import initialize_cube_localization
from easy_cozmo.movements import _move_lift, _move_head
#del speed_mmps
from mygotopose import *
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
from easy_cozmo.odometry import set_odom_origin, get_odom_pose, reset_odometry
from easy_cozmo.easy_cozmo import run_program_with_viewer, run_program
from easy_cozmo.animations import show_victory
import math
import cozmo
_poses = []
_tour = []
_navigating = False
_nav_action = None
_current_nav_pose = None
_success = False

def error(msg):
    try:
        say_error(msg)
    except:
        pass


def read_tour(fname):
    global _tour
    f = open(fname)
    _tour = []
    for lines in f.readlines():
        s = lines.split()
        if len(s) > 0:
            _tour.append(int(s[0]))
    f.close()
    print("READ TOUR of ", len(_tour), " sites")
    return len(_tour)

def tour_str():
    str=""
    for l in _tour:
        str=str + "%d "%(l)
    return str

def read_locations(fname):
    global _poses
    f = open(fname)
    for lines in f.readlines():
        s = lines.split()
        if len(s) > 1:
            _poses.append((float(s[0]), float(s[1])))
    f.close()
    print("READ ", len(_poses), " POSES")
    return len(_poses)

def risk_of_collision():
    return False

def loc(index):
    return _tour[index-1]

def initialize(use_server=False, server="localhost"):
    #mc._mycozmo.set_robot_volume(.1)
    # TODO: make use of server optional
    mc._robot.world.undefine_all_custom_marker_objects()
    mc._robot.go_to_pose_factory = MyGoToPose
    set_odom_origin(*_poses[_tour[0]])
    initialize_cube_localization()
    _move_lift(0.1)
    _move_head(degrees(20))
    enable_head_light()

def initialize_nav():
    set_odom_origin(*_poses[_tour[0]])
    reset_odometry()
    _move_lift(0.1)
    _move_head(degrees(20))
    enable_head_light()
    _navigating = False
    nav_action = None
    _current_nav_pose = None
    _success = False


def check_distance():
#    return False
    odom_pose = get_odom_pose()
    d_pose = _current_nav_pose - odom_pose
    dst = d_pose.position.x ** 2 + d_pose.position.y ** 2
    dst = dst ** 0.5
    #print("distance to target : ", dst)
    if dst < 25:
        #print("close enough, break")
        return True
    return False



def navigating():
    global _navigating, _success
    if _nav_action is None:
        return False
    if _nav_action.is_running:
        pause(0.2)
        if check_distance():
            _nav_action.abort()
            _navigating = False
            _success=True
            return False
        else:
            return True
    else:
        _navigating = False
    return _navigating

def navigation_successful():
    if _nav_action is None:
        return False
    if _nav_action.is_running:
        return False
    return _nav_action.has_succeeded or _success

def collect_reward(index):
    try:
        mc._robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabWhoa).wait_for_completed()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)


def celebrate():
    show_victory()

def pause_navigation():
    global _navigating
    _nav_action.abort()
    _navigating = False

def resume_navigation():
    if _current_dest is not None:
        return navigate_to(_current_dest)

def navigate_to2(ix):
    global _success
    global _navigating, _nav_action
    global _current_dest, _current_nav_pose
    x, y = _poses[_tour[ix-1]]
    _move_lift(0.1)
    _move_head(degrees(0))

    _success = False
    #print("Going to ", x, y)
    p_pose = Pose(int(x*10), int(y*10), 0, angle_z=degrees(0))
    odom_pose = get_odom_pose()
    #print("odom_pose ", odom_pose)
    #print("p_pose ", p_pose)
    d_pose = p_pose - odom_pose
    #print("d_pose ", d_pose)
    theta = -1*odom_pose.rotation.angle_z.radians
    #print("theta ", theta)
    rx = d_pose.position.x* math.cos(theta) - d_pose.position.y*math.sin(theta)
    ry = d_pose.position.x* math.sin(theta) + d_pose.position.y*math.cos(theta)
    r_pose = Pose(int(rx), int(ry), 0, angle_z=degrees(0))
    #print("r_pose ", r_pose)
    _navigating = True
    _current_dest = ix

    _current_nav_pose = p_pose
    try:
        _nav_action = mc._robot.go_to_pose(r_pose, relative_to_robot=True,
                                           num_retries=1)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        _navigating = False
        _nav_action.abort()
    return _navigating

def _rotate_in_place(angle, rot_speed=8):
    """**Rotate in place for a given angle in degrees**

    :param angle: Rotation angle (in degrees)
    :type angle: float

    :return: True (succeeded) or False (failed)
    """

    if abs(angle-0) < 0.01:
        return True
    action = mc._robot.turn_in_place(radians(angle),speed=degrees(rot_speed))
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


def navigate_to3(ix):
    global _success
    global _navigating, _nav_action
    global _current_dest, _current_nav_pose
    x, y = _poses[_tour[ix-1]]
    _move_lift(0.1)
    _move_head(degrees(0))

    _success = False
    #print("Going to ", x, y)



    dest_pose = Pose(int(x*10), int(y*10), 0, angle_z=degrees(0))
    odom_pose = get_odom_pose()


    #print("odom_pose ", odom_pose)
    #print("p_pose ", p_pose)
    d_pose = dest_pose - odom_pose
    dst = d_pose.position.x ** 2 + d_pose.position.y ** 2
    dst = dst ** 0.5
    #print("distance to target : ", dst)
    """ only do rotation if far """
    if dst > 45:
        alpha = odom_pose.rotation.angle_z.radians

        theta = math.atan2(d_pose.position.y, d_pose.position.x) - alpha;
        if theta > math.pi:
            theta -= 2 * math.pi
        elif theta <= -math.pi:
            theta += 2 * math.pi

        _rotate_in_place(theta)

    odom_pose = get_odom_pose()
    alpha = odom_pose.rotation.angle_z.radians

    d_pose = dest_pose - odom_pose
    theta = math.atan2(d_pose.position.y, d_pose.position.x) - alpha;
    if theta > math.pi:
        theta -= 2 * math.pi
    elif theta <= -math.pi:
        theta += 2 * math.pi


    alpha = -1*odom_pose.rotation.angle_z.radians
    #print("theta ", theta)
    rx = d_pose.position.x* math.cos(alpha) - d_pose.position.y*math.sin(alpha)
    ry = d_pose.position.x* math.sin(alpha) + d_pose.position.y*math.cos(alpha)
    r_pose = None
    if dst > 45 and _current_nav_pose != None :
        r_pose = Pose(rx, ry, 0, angle_z=radians(theta))
    else:
        r_pose = Pose(rx, ry, 0, angle_z=radians(0))

    #print("Current pose ", odom_pose)
    #print("dest_pose ", dest_pose)
    #print("r_pose ", r_pose)

    _navigating = True
    _current_dest = ix
    _current_nav_pose = dest_pose
    try:
        _nav_action = mc._robot.go_to_pose(r_pose, relative_to_robot=True,
                                           num_retries=1)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        _navigating = False
        _nav_action.abort()
    return _navigating



def navigate_to(ix):
    global _success
    global _navigating, _nav_action
    global _current_dest, _current_nav_pose
    x, y = _poses[_tour[ix-1]]
    _success = False
    #print("Going to ", x, y)
    p_pose = Pose(int(x*10), int(y*10), 0, angle_z=degrees(0))
    odom_pose = get_odom_pose()
    d_pose = p_pose - odom_pose
    #print("odom_pose ", odom_pose)
    #print("d_pose ", d_pose)
    _navigating = True
    _current_dest = ix
    _current_nav_pose = p_pose
    try:
        _nav_action = mc._robot.go_to_pose(d_pose, relative_to_robot=True,
                                           num_retries=1)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        _navigating = False
        _nav_action.abort()
    return _navigating

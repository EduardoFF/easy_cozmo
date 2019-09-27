# -*- coding: utf-8 -*-

import asyncio
import cozmo
import cv2 as cv
import numpy as np
import math
import sys
from .ball_detection_utils import *
from .defaults import *
from PIL import Image, ImageDraw, ImageFont
from . import easy_cozmo
from .movements import _move_head, move_lift_ground,_execute_go_to_pose, set_wheels_speeds, stop, move_head_looking_forward
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes, CustomObjectMarkers
from .robot_utils import pause
from .robot_utils import enable_head_light, disable_head_light
from .say import *
import time
from .odometry import *
from .actions_with_cubes import scan_for_cube_by_id, _get_visible_cube_by_id, _get_relative_pose, _get_localized_cube_by_id,distance_to_cube
from .actions_with_custom_markers import scan_for_marker_by_id, _get_visible_marker_by_id, center_marker, _get_localized_marker_by_id, distance_to_marker
_ball_detector = None
_df_scan_ball_speed = 17 #in degrees
_at_home = False
_ball_detection_initialized = False

_post_marker_registered = False
_is_marker_registered = False
_marker_type = CustomObjectMarkers.Circles2
_marker_size = 120
_marker_id = CustomObjectTypes.CustomType01
_left_post_marker_id = CustomObjectTypes.CustomType02
_right_post_marker_id = CustomObjectTypes.CustomType03
_marker_height = 150
_last_marker_obj = None
if _at_home:
    """
    _df_hl = 0
    _df_hh = 4
    _df_sl = 143
    _df_sh = 255
    _df_vl = 75
    _df_vh = 147
    _df_gain = 1
    _df_exp = 4
    """
    _df_hl = 0
    _df_hh = 4
    _df_sl = 193
    _df_sh = 255
    _df_vl = 160
    _df_vh = 255
    _df_gain = 0.77
    _df_exp = 44

else:
    _df_hl = 0
    _df_hh = 11
    _df_sl = 122#160
    _df_sh = 255
    _df_vl = 120
    _df_vh = 255
    _df_gain = 1
    _df_exp = 15

    """
    _df_hl = 0
    _df_hh = 14
    _df_sl = 193
    _df_sh = 255
    _df_vl = 75
    _df_vh = 255
    _df_gain = 1
    _df_exp = 14
    """

_df_cs_low = np.array([_df_hl,_df_sl,_df_vl], dtype="uint8")
_df_cs_high = np.array([_df_hh,_df_sh,_df_vh], dtype="uint8")


_fx,_fy = 277.345389059622  ,278.253264643578
_cx,_cy = 152.389201831827, 109.376457506074
_df_camera_mtx=np.array([[_fx,0,_cx],
                         [0,_fy,_cy],
                         [0,0,1]])
_k1,_k2=-0.0691655300978844,0.0630063731358772
_p1,_p2=0,0
_cam_dist=np.array([_k1,_k2,_p1,_p2])

""" Pid auto exposure control """
class AutoExposureAlgo:
    def __init__(self, robot):
        self.robot = robot
        self.KPe = 0.005
        self.KIe = 0.01
        self.KDe = self.KPe
        self.KPg = 0.0001
        self.KIg = 0.01
        self.KDg = self.KPg

        self.prev_mu = None
        self.prev_sigma = None
        self.target_mu = 140
        self.prev_err = 0
        self.rate = 2
        self.cnt = 0
        self.current_exposure = self.robot.camera.exposure_ms
        self.current_gain = self.robot.camera.gain
        self.stabilized = False


    def set_target(self, tgt):
#        return
        self.target_mu = tgt

    def gain_control(self):
        current_gain = self.robot.camera.gain
        new_gain =  current_gain +  self.err * self.KPg + self.prev_err * self.KDg
        #print("GAIN: ", new_gain)
        return new_gain
    def exposure_control(self):
        current_exposure = self.robot.camera.exposure_ms
        new_exposure =  current_exposure +  self.err * self.KPe + self.prev_err * self.KDe
        #print("EXPOSURE: ", new_exposure)
        return new_exposure


    def proc_image(self,raw_image):
        from scipy.stats import norm
        #import matplotlib.mlab as mlab

        self.cnt +=1
        if self.cnt <= self.rate:
            return None, None
        self.cnt = 0

        raw_img = np.array(raw_image)
        g = raw_img[:,:,1]
        (mu, sigma) =  norm.fit(g.ravel())
#        print("GAUSSIAN FIT: ", mu,sigma)
        self.err = self.target_mu -  mu
        #current_exposure = self.robot.camera.exposure_ms
        #current_gain = self.robot.camera.gain
        current_gain = self.current_gain
        current_exposure = self.current_exposure
        #print("C EXPOSURE ", current_exposure)
        #print("C GAIN ", current_gain)

        new_gain = current_gain
        new_exposure = current_exposure
        #print("ERR ", self.err)
        # 5 units of error
        if abs(self.err)/self.target_mu > 0.1:
            exposure_saturated = current_exposure >= self.robot.camera.config.max_exposure_time_ms or current_exposure <= self.robot.camera.config.min_exposure_time_ms
            if abs(new_gain - 1.0) > 0.1 and exposure_saturated:
                new_gain = self.gain_control()
            else:
                new_exposure =  self.exposure_control()
                if new_exposure >= self.robot.camera.config.max_exposure_time_ms or new_exposure <= self.robot.camera.config.min_exposure_time_ms:
                    new_gain = self.gain_control()

            """ check bounds """
            if new_exposure > self.robot.camera.config.max_exposure_time_ms:
                new_exposure = self.robot.camera.config.max_exposure_time_ms
            if new_exposure < self.robot.camera.config.min_exposure_time_ms:
                new_exposure = self.robot.camera.config.min_exposure_time_ms
            if new_gain > self.robot.camera.config.max_gain:
                new_gain = self.robot.camera.config.max_gain
            if new_gain < self.robot.camera.config.min_gain:
                new_gain = self.robot.camera.config.min_gain
            s_exposure = round(new_exposure)
            self.current_exposure = new_exposure
            s_gain = round(new_gain * 100) / 100.
            self.current_gain = new_gain
            #print("SETTING MANUAL EXPOSURE", new_exposure, new_gain)
            self.robot.camera.set_manual_exposure(s_exposure, s_gain)
        else:
            self.stabilized = True
        self.prev_err = self.err
        return new_gain, new_exposure


class BallAnnotator(cozmo.annotate.Annotator):
    def __init__(self, detector):
        super(BallAnnotator, self).__init__(detector._robot.world.image_annotator)
        self._detector = detector
    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        ret = _ball_detector.get_avg_img_vals()
        if ret is not None:
            (cx,cy), r = ret
            x1 = (cx-r)*scale
            x2 = (cx+r)*scale
            y1 = (cy-r)*scale
            y2 = (cy+r)*scale
            d.ellipse((x1, y1, x2, y2), outline ='green')
            rad=5
            x1 = (cx-rad)*scale
            x2 = (cx+rad)*scale
            y1 = (cy-rad)*scale
            y2 = (cy+rad)*scale
            d.ellipse((x1, y1, x2, y2), fill = 'red', outline ='red')
        bounds = (0, 0, image.width, image.height)
        distance = self._detector.get_avg_distance()
        if distance is not None:
            text = None
            try:
                arialfont = ImageFont.truetype("arial.ttf", 28, encoding="unic")
                if arialfont != None:
                    text = cozmo.annotate.ImageText('DISTANCE %d \u00b0 ' % distance, font=arialfont, color='green')
            except:
                pass
            if text is None:
                text = cozmo.annotate.ImageText('DISTANCE %d \u00b0 ' % distance, color='green')
            text.render(d, bounds)


class BallDetector:
    def __init__(self, robot, autoexposure=True):
        self._robot = robot
        self._ma_img_center_dev = []
        self.center = None
        self.img_centers = []
        self.img_radius = []
        self.distance = None
        self.distances = []
        self.autoexposure_algo = None
        if autoexposure:
            print("Using autoexposure")
            self.autoexposure_algo = AutoExposureAlgo(robot)
        self._robot.add_event_handler(cozmo.world.EvtNewCameraImage, self.on_img)
        self.anno = BallAnnotator(self)
        self._robot.world.image_annotator.add_annotator('balldetect', self.anno)

    def is_autoexposure_enabled(self):
        return self.autoexposure_algo is not None
    def is_autoexposure_stabilized(self):
        return self.is_autoexposure_enabled() and self.autoexposure_algo.stabilized


    def on_img(self, event, *, image:cozmo.world.CameraImage, **kw):
        raw_img = image.raw_image
        raw_rgb = np.array(raw_img)
        cv2_image = cv.cvtColor(raw_rgb, cv.COLOR_RGB2BGR)
        height, width, channels = cv2_image.shape
        #print(height,width)
        if self.autoexposure_algo is not None:
            """ pass the current raw image in order to do
            auto exposure (valid in the  next iteration)"""
            self.autoexposure_algo.proc_image(raw_img)

        args = {'rho': df_houghdetector_rho,
                'theta_div': df_houghdetector_thetadiv,
                'threshold': df_houghdetector_threshold,
                'minLineLength': df_houghdetector_minlinelength,
                'maxLineGap': df_houghdetector_maxlinegap,
                'lane_detection': df_houghdetector_lanedetection,
                'single_line_output': df_houghdetector_singlelineoutput,
                'draw_single_line':False,
                'hsv_low': _df_cs_low,
                'hsv_high': _df_cs_high,
                'draw_lines':False}
        detected, proc_cv_image, center, rad  = detect_ball(cv2_image,
                                                            tag=False,
                                                            **args)
        #print("Detected ",detected)
        distance = None
        if detected:
            #print(center,rad)
            ret, rvecs, tvecs = get_ball_pnp(center, rad)
            if ret:
                distance = np.linalg.norm(tvecs)
                #print("Distance ",self.distance)
                #self._ma_img_center_dev.append(160 - center[0])
        self.img_centers.append(center)
        self.img_radius.append(rad)
        self.distances.append(distance)
        if len(self.img_centers) > 10:
            self.img_centers = self.img_centers[-10:]
        if len(self.img_radius) > 10:
            self.img_radius = self.img_radius[-10:]
        if len(self.distances) > 10:
            self.distances = self.distances[-10:]

        self.center = center
        self.rad = rad
        self.distance = distance
        if len(self._ma_img_center_dev) > 10:
            self._ma_img_center_dev = self._ma_img_center_dev[-10:]

    def get_avg_distance(self):
        dists=[d for d in self.distances if d is not None]
        if len(dists) > 0:
            w = np.arange(1,len(dists)+1)
            d = np.average(np.array(dists), weights=w)
            return d
        else:
            return None

    def get_avg_img_vals(self):
        centers=[c for c in self.img_centers if c is not None]
        rads = [r for r in self.img_radius if r is not None]

        if len(centers) > 0:
            w = np.arange(1,len(centers)+1)
            cx = np.average(np.array([c[0] for c in centers]), weights=w)
            cy = np.average(np.array([c[1] for c in centers]), weights=w)
            r = np.average(rads, weights=w)
            return (cx,cy),r
        else:
            return None


def init_ball_detection():
    global _ball_detection_initialized
    if _ball_detection_initialized:
        return True
    from .odometry import initialize_odometry
    _initialize_ball_detector()
    initialize_odometry()
    _ball_detection_initialized = True
    return _ball_detection_initialized

def init_post_marker_registration():
    global _post_marker_registered
    robot = easy_cozmo._robot
    if _post_marker_registered:
        return True

    robot.world.define_custom_cube(_left_post_marker_id,
                                              CustomObjectMarkers.Circles3,
                                              49,
                                              45, 45, True)
    robot.world.define_custom_cube(_right_post_marker_id,
                                              CustomObjectMarkers.Diamonds3,
                                              49,
                                              45, 45, True)

    _post_marker_registered = True
    pause(2)



def _initialize_ball_detector():
    import time
    global _ball_detector
    robot = easy_cozmo._robot
    set_camera_for_ball()
    robot.camera.set_manual_exposure(8,0.8)
    _move_head(degrees(-11))
    #robot.set_head_angle(Angle(degrees=4)).wait_for_completed()
    _ball_detector = BallDetector(robot)
    tt = time.time()
    while time.time() - tt < 5:
        if _ball_detector.is_autoexposure_stabilized():
            print("AUTOEXPOSURE STABILIZED")
            break
        time.sleep(.2)

def is_stable_detection():
    norms = [np.linalg.norm(np.array([c[0],c[1]])) for c in _ball_detector.img_centers if c is not None]
    rads = np.array([r for r in _ball_detector.img_radius if r is not None])
    #print("norms",norms)
    stddev=np.std(norms)
    #print("stddev",stddev)
    if len(norms) > 4 and stddev < 20 and np.std(rads) < 5:
        return True
    return False

def scan_for_ball(angle, scan_speed=_df_scan_ball_speed):
    """**Rotate in place while looking for the ball**

    This function executes a rotation, with certain angular speed
    and angle, while at the same time looking for the ball.  As
    soon as Cozmo identifies the balll in its field of view (not
    necessarily at the center of the camera), it stops.  As a
    result, Cozmo will keep seeing the ball after it stops.

    :param angle: Angle to scan
    :type angle: float

        ..  note::

            If the angle is positive, Cozmo rotates in clockwise order. A
    negative angle is a counter clockwise rotation. :param scan_speed: Scan
    speed, defaults to :_df_scan_ball_speed: :type scan_speed: float, optional

    :return: True (suceeded) or False (failed).

    """

    # makes positive angles cw
    set_camera_for_ball()
    if not init_ball_detection():
        say_error("Ball detection can't be initilized")
        return False


    angle *= -1
    robot = easy_cozmo._robot
    _move_head(degrees(-11))
    pause(0.5)
    action = robot.turn_in_place(degrees(angle), speed=degrees(scan_speed))
    while( not is_stable_detection()):
            if action.is_completed:
                print("Action completed")
                break
            time.sleep(.2)
    try:
            while action.is_running:
                    action.abort()
                    time.sleep(.5)

    except Exception as e:
            import traceback
            print(e)
            traceback.print_exc()
            say_error("Scan for ball failed")
    return is_stable_detection()

def compute_hor_dev():
    errors_n = [(160 - c[0]) for c in _ball_detector.img_centers if c is not None]
    #print("errors_n ", errors_n)
    if len(errors_n) > 0:
        w = []
        for i in range(len(errors_n)):
            w.append(2**i)
        e = np.mean(np.array(errors_n))
        #print("error ", e)
        return e, np.std(errors_n)
    else:
        return None,None

def last_err():
    errors_n = [(160 - c[0]) for c in _ball_detector.img_centers if c is not None]
    #print("errors_nx ", errors_n)
    if len(errors_n) == 0:
        return None
    if len(errors_n) == 1:
        return errors_n[0]
    e = np.mean(np.array(errors_n[-2:]))
    #_debug("last_error ", e)
    return e

def is_ball_visible():
    return is_stable_detection()

def distance_to_ball():
    """**Get the distance (in mm) to the ball**

    ..  note::

    If cozmo cannot see the ball it will trigger an error and return an invalid
    distance value, be sure to check if the ball is visible using
    :is_ball_visible: before calling this function

    :return: The distance in mm or an invalid value (None)

    """
    if not init_ball_detection():
        say_error("Ball detection can't be initilized")
        return None

    if not is_stable_detection():
        say_error("Ball not detected")
        return None
    return _ball_detector.get_avg_distance()


def __align_with_ball():
    robot = easy_cozmo._robot
    if not init_ball_detection():
        say_error("Ball detection can't be initilized")
        return False
    if not is_stable_detection():
        say_error("Ball not detected")
        return False


    def make_speed(s):
        if s > 10:
            s = 10
        if s < -10:
            s = -10
        return s

    err, std = compute_hor_dev()
    if not err:
        say_error("Ball not detected")
        return False
    current_speed_l = 0
    current_speed_r = 0
    #print("Initial error", err)
    timeout = False
    start_t = time.time()
    sum_error = 0
    prev_err = 0
    KP = 0.25
    KI = 0.01
    KD = KP

    while (abs(err) > 5 or abs(std) > 5) and not timeout:
        err, std = compute_hor_dev()
        if not err:
            say_error("Ball lost")
            return False
        if abs(err) < 5 and abs(std) < 5:
            #print("RESET")
            current_speed_l = 0
            current_speed_r = 0
            sum_error = 0
            prev_err = 0
            robot.stop_all_motors()
            break
        if not err:
            say_error("Ball not detected")
            return False
        err = last_err()
        #print("error: ",err)
        if err is None:
            return False
        current_speed_l -= (err * KP + sum_error * KI + prev_err * KD)
        current_speed_r += (err * KP + sum_error * KI +  prev_err * KD)
        sum_error += err
        prev_err = err
        current_speed_l = make_speed(current_speed_l)
        current_speed_r = make_speed(current_speed_r)
        #print("speed l {:2f} r {:2f}".format(current_speed_l, current_speed_r))
        robot.drive_wheel_motors(current_speed_l, current_speed_r)
        if time.time() > start_t + 100:
            print("TIMEOUT")
            timeout = True
        time.sleep(0.05)

    robot.stop_all_motors()
    if not is_stable_detection():
        return False
    err, std = compute_hor_dev()
    print("FINAL ERR: ",err, std)
    return abs(err) <6

def set_camera_for_ball():

    robot = easy_cozmo._robot
    if _ball_detector is not None and _ball_detector.is_autoexposure_enabled():
        _ball_detector.autoexposure_algo.set_target(120)
        return

    robot.camera.image_stream_enabled = False
    robot.camera.enable_auto_exposure(False)
    #robot.camera.set_manual_exposure(_df_exp,_df_gain)
    robot.set_head_light(False)
    robot.camera.color_image_enabled = True
    pause(1)
    robot.camera.image_stream_enabled = True

def set_camera_for_cube():
    if _ball_detector is not None and _ball_detector.is_autoexposure_enabled():
        _ball_detector.autoexposure_algo.set_target(140)
        return

    return
    robot = easy_cozmo._robot
    robot.camera.image_stream_enabled = False
    robot.camera.enable_auto_exposure(True)
    #robot.camera.set_manual_exposure(30,2)
    #robot.set_head_light(True)
    robot.camera.color_image_enabled = False
    robot.camera.image_stream_enabled = True
    pause(1)


def align_with_ball2():
    if not init_ball_detection():
        say_error("Ball detection can't be initilized")
        return False

    robot = easy_cozmo._robot
    set_camera_for_ball()
    pause(1)
    err, std = compute_hor_dev()
    timeout = False
    start_t = time.time()
    while not timeout:
        err, std = compute_hor_dev()
        if err is None:
            return False
        #print("Hor dev ", err, std)
        if abs(err) < 10 and abs(std) < 5:
            break
        err = last_err()
        if err is None:
            return False
        if err < 0:
            err = -1
        else:
            err = 1

        action = robot.turn_in_place(degrees(3*err), speed=degrees(5))
        while True:
                if action.is_completed:
                        break
                err = last_err()
                if err is None:
                    break
                if abs(err) < 10:
                    break
                time.sleep(.2)
        try:
                while action.is_running:
                        action.abort()
                        time.sleep(.5)

        except Exception as e:
                import traceback
                print(e)
                traceback.print_exc()
                say_error("Scan for object failed")
        if err is None:
            return False
        if time.time() > start_t + 30:
            print("TIMEOUT")
            timeout = True

    return is_stable_detection()

def align_with_ball():
    return align_with_ball2()

def fix_virtual_ball_in_world(position, ball_diameter=40):
    robot = easy_cozmo._robot
    pose = Pose(position[0], position[1], 0, angle_z=degrees(0))
    pose.origin_id = robot.pose.origin_id
    robot.world.delete_fixed_custom_objects()
    pause(0.5)
    #print("Creating virtual ball @ ", pose)
    fixed_object = robot.world.create_custom_fixed_object(pose, ball_diameter,
                                                          ball_diameter,
                                                          ball_diameter,
                                                          relative_to_robot=True)
    if not fixed_object:
        say_error("Can't create fixed object")

    pause(1)  # play safe


def center_ball():
    _move_head(degrees(-11))
    return align_with_ball2()

def align_ball_and_cube(cube_id):
    if not init_ball_detection():
        say_error("Ball detection can't be initilized")
        return False

    robot = easy_cozmo._robot
    if scan_for_ball(360):
        #print("FOUND BALL")
        if align_with_ball2():
            reset_odometry()
            #print("ALIGNED WITH BALL")
            distance = distance_to_ball()
            if distance == None:
                say_error("Can't estimate distance")
                return False
            set_camera_for_cube()
            cube = None
            cube =  _get_localized_cube_by_id(cube_id)
            if cube is None:
                if scan_for_cube_by_id(360, cube_id):
                    cube = _get_visible_cube_by_id(cube_id)
            if cube is not None:
                rel_pose = _get_relative_pose(cube.pose, robot.pose)
                #print("RELATIVE POSE ", rel_pose)
                odom_pose = get_odom_pose()
                #print("ODOM POSE ", odom_pose)
                alpha = odom_pose.rotation.angle_z.radians
                ball_pose = (distance*math.cos(-1*alpha), distance*math.sin(-1*alpha))
                #print("BALL POSE ", ball_pose)
                cube_pose = (rel_pose.position.x, rel_pose.position.y)
                #print("CUBE POSE ", cube_pose)
                angle = math.atan2(ball_pose[1]-cube_pose[1], ball_pose[0]-cube_pose[0])
                dist = 100

                new_pose = (ball_pose[0] + dist*math.cos(angle),
                            ball_pose[1] + dist*math.sin(angle))
                fix_virtual_ball_in_world(ball_pose, 60)
                #print("GOING TO ",new_pose)
                pose = Pose(new_pose[0], new_pose[1], 0, angle_z=radians(angle+math.pi))
                ret = _execute_go_to_pose(pose)
                if not ret:
                    return False
                if align_with_ball2():
                    rel_pose = _get_relative_pose(cube.pose, robot.pose)
                    #print("2ND RELATIVE POSE ", rel_pose)
                    distance = distance_to_ball()
                    if distance == None:
                        say_error("Can't estimate distance")
                        return False

                    ball_pose = (distance, 0)
                    #print("BALL POSE ", ball_pose)
                    cube_pose = (rel_pose.position.x, rel_pose.position.y)
                    #print("CUBE POSE ", cube_pose)
                    angle = math.atan2(ball_pose[1]-cube_pose[1], ball_pose[0]-cube_pose[0])
                    dist = 100

                    new_pose = (ball_pose[0] + dist*math.cos(angle),
                                ball_pose[1] + dist*math.sin(angle))
                    fix_virtual_ball_in_world(ball_pose, 60)
                    #print("GOING TO ",new_pose)
                    pose = Pose(new_pose[0], new_pose[1], 0, angle_z=radians(angle+math.pi))
                    ret = _execute_go_to_pose(pose)
                    if not ret:
                        return False
                    else:
                        return True
            else:
                say_error("Can't find cube {}".format(cube_id))
                return False
        else:
            say_error("Can't align with ball")
            return False
    else:
        say_error("Can't find ball")
        return False
    return True

def align_with_ball_and_cube(cube_id):
    return align_ball_and_cube(cube_id)

def align_ball_and_marker(marker_id):
    if not init_ball_detection():
        say_error("Ball detection can't be initilized")
        return False

    robot = easy_cozmo._robot
    if scan_for_ball(360):
        #print("FOUND BALL")
        if align_with_ball2():
            reset_odometry()
            #print("ALIGNED WITH BALL")
            distance = distance_to_ball()
            if distance == None:
                say_error("Can't estimate distance")
                return False
            set_camera_for_cube()
            marker = None
            marker =  _get_localized_marker_by_id(marker_id)
            if marker is None:
                if scan_for_marker_by_id(360, marker_id):
                    marker = _get_visible_marker_by_id(marker_id)
            if marker is not None:
                rel_pose = _get_relative_pose(marker.pose, robot.pose)
                #print("RELATIVE POSE ", rel_pose)
                odom_pose = get_odom_pose()
                #print("ODOM POSE ", odom_pose)
                alpha = odom_pose.rotation.angle_z.radians
                ball_pose = (distance*math.cos(-1*alpha), distance*math.sin(-1*alpha))
                #print("BALL POSE ", ball_pose)
                marker_pose = (rel_pose.position.x, rel_pose.position.y)
                #print("MARKER POSE ", marker_pose)
                angle = math.atan2(ball_pose[1]-marker_pose[1], ball_pose[0]-marker_pose[0])
                dist = 100

                new_pose = (ball_pose[0] + dist*math.cos(angle),
                            ball_pose[1] + dist*math.sin(angle))
                fix_virtual_ball_in_world(ball_pose, 60)
                #print("GOING TO ",new_pose)
                pose = Pose(new_pose[0], new_pose[1], 0, angle_z=radians(angle+math.pi))
                ret = _execute_go_to_pose(pose)
                if not ret:
                    return False
                if align_with_ball2():
                    rel_pose = _get_relative_pose(marker.pose, robot.pose)
                    #print("2ND RELATIVE POSE ", rel_pose)
                    distance = distance_to_ball()
                    if distance == None:
                        say_error("Can't estimate distance")
                        return False

                    ball_pose = (distance, 0)
                    #print("BALL POSE ", ball_pose)
                    marker_pose = (rel_pose.position.x, rel_pose.position.y)
                    #print("MARKER POSE ", marker_pose)
                    angle = math.atan2(ball_pose[1]-marker_pose[1], ball_pose[0]-marker_pose[0])
                    dist = 100

                    new_pose = (ball_pose[0] + dist*math.cos(angle),
                                ball_pose[1] + dist*math.sin(angle))
                    fix_virtual_ball_in_world(ball_pose, 60)
                    #print("GOING TO ",new_pose)
                    pose = Pose(new_pose[0], new_pose[1], 0, angle_z=radians(angle+math.pi))
                    ret = _execute_go_to_pose(pose)
                    if not ret:
                        return False
                    else:
                        return True
            else:
                say_error("Can't find marker {}".format(marker_id))
                return False
        else:
            say_error("Can't align with ball")
            return False
    else:
        say_error("Can't find ball")
        return False
    return True

def align_with_ball_and_marker(marker_id):
    return align_ball_and_marker(marker_id)

def _kick1(distance=240, ball_diam=40, speed=200):
    robot = easy_cozmo._robot
    dur = distance/speed
    robot.drive_wheel_motors(int(speed), int(speed),\
                             l_wheel_acc=400, r_wheel_acc=400)

    pause(dur)
    robot.stop_all_motors()
    return True

def kick_ball(distance=100, ball_diam=40):
    _kick1(distance=distance, ball_diam=ball_diam)

def kick(distance=100, ball_diam=40):
    if center_ball():
        d = distance_to_ball()
        #print("d = ",d)
        if d is None:
            say_error("No ball found")
            return False
        return _kick1(distance=d+100, ball_diam=ball_diam)
    else:
        say_error("No ball found")
        return False

def touch_ball(distance=200, ball_diam=40):
    _kick1(distance=distance, ball_diam=ball_diam, speed=100)

def _is_goal_marker_registered():
    return _is_marker_registered

def register_goal_marker():
    global _is_marker_registered
    robot = easy_cozmo._robot
    robot.world.define_custom_wall(_marker_id,
                                   _marker_type,
                                   _marker_size, _marker_size,
                                   _marker_size, _marker_size, True)
    _is_marker_registered = True

def _last_goal_pose_valid():
    robot = easy_cozmo._robot
    if _last_marker_obj is None:
        return False
    return _last_marker_obj.pose.origin_id != -1 and robot.pose.origin_id == _last_marker_obj.pose.origin_id

def move_head_towards_goal():
    robot = easy_cozmo._robot
    translation = robot.pose - _last_marker_obj.pose
    dst = translation.position.x ** 2 + translation.position.y ** 2
    dst = dst ** 0.5
    angle = math.atan2(_marker_height - 25, dst)
    #print("HEAD ANGLE TO GOAL ", math.degrees(angle))
    _move_head(radians(angle))


def scan_for_goal(angle):
    global _last_marker_obj
    set_camera_for_cube()
    #move_head_looking_forward()
    if _last_goal_pose_valid():
        #print("GOAL POSE VALID")
        move_head_towards_goal()
    _move_head(degrees(10))
    if not _is_goal_marker_registered():
        register_goal_marker()
    if scan_for_marker_by_id(angle, _marker_id, use_distance_threshold=False):
        _last_marker_obj = _get_goal()
        return True
    else:
        return False

def _get_goal():
    _move_head(degrees(10))
    return _get_visible_marker_by_id(_marker_id, use_distance_threshold=False)

def distance_to_goal():
    _move_head(degrees(10))
    goal = _get_visible_marker_by_id(_marker_id, use_distance_threshold=False)
    if goal is None:
        return None
    robot = easy_cozmo._robot
    translation = robot.pose - goal.pose
    dst = translation.position.x ** 2 + translation.position.y ** 2
    dst = dst ** 0.5
    return dst

def _align_ball_and_goal():
    robot = easy_cozmo._robot
    set_camera_for_cube()
    move_head_looking_forward()
    if scan_for_goal(360):
        #print("GOAL FOUND")
        if center_marker(_marker_id, use_distance_threshold=False):
            move_head_looking_forward()
            reset_odometry()
            #print("ALIGNED WITH GOAL")
            distance = distance_to_goal()
            if distance == None:
                say_error("Can't estimate distance")
                return False
            marker = _get_goal()
            if marker is None:
                say_error("Can't detect goal")
                return False
            set_camera_for_ball()
            if scan_for_ball(360) and align_with_ball2():
                d2 = distance_to_ball()
                if d2 is None:
                    say_error("Can't estimate distance to ball")
                    return False
                odom_pose = get_odom_pose()
                #print("ODOM POSE ", odom_pose)
                alpha = odom_pose.rotation.angle_z.radians
                marker_pose = (distance*math.cos(-1*alpha),
                               distance*math.sin(-1*alpha))

                #print("MARKER POSE ", marker_pose)
                ball_pose = (d2, 0)
                #print("BALL POSE ", ball_pose)
                angle = math.atan2(ball_pose[1]-marker_pose[1],
                                   ball_pose[0]-marker_pose[0])
                dist = 100

                new_pose = (ball_pose[0] + dist*math.cos(angle),
                            ball_pose[1] + dist*math.sin(angle))
                fix_virtual_ball_in_world(ball_pose, 60)
                #print("GOING TO ",new_pose)
                pose = Pose(new_pose[0], new_pose[1], 0,
                            angle_z=radians(angle+math.pi))
                ret = _execute_go_to_pose(pose)
                if not ret:
                    return False
                if align_with_ball2():
                    rel_pose = _get_relative_pose(marker.pose, robot.pose)
                    #print("2ND RELATIVE POSE ", rel_pose)
                    distance = distance_to_ball()
                    if distance == None:
                        say_error("Can't estimate distance")
                        return False

                    ball_pose = (distance, 0)
                    #print("BALL POSE ", ball_pose)
                    marker_pose = (rel_pose.position.x, rel_pose.position.y)
                    #print("MARKER POSE ", marker_pose)
                    angle = math.atan2(ball_pose[1]-marker_pose[1],
                                       ball_pose[0]-marker_pose[0])
                    dist = 100

                    new_pose = (ball_pose[0] + dist*math.cos(angle),
                                ball_pose[1] + dist*math.sin(angle))
                    fix_virtual_ball_in_world(ball_pose, 60)
                    #print("GOING TO ",new_pose)
                    pose = Pose(new_pose[0], new_pose[1], 0, angle_z=radians(angle+math.pi))
                    ret = _execute_go_to_pose(pose)
                    if not ret:
                        return False
                    else:
                        return True
            else:
                say_error("Can't find goal")
                return False
        else:
            say_error("Can't align with goal")
            return False
    else:
        say_error("Can't find goal")
        return False
    return True

def scan_for_left_post(angle):
#    init_post_marker_registration()
    return scan_for_cube_by_id(360, 1)
#    return scan_for_marker_by_id(angle, _left_post_marker_id , use_distance_threshold=False)

def scan_for_right_post(angle):
#    init_post_marker_registration()
    return scan_for_cube_by_id(360, 2)
#    return scan_for_marker_by_id(angle, _right_post_marker_id , use_distance_threshold=False)

def distance_to_left_post():
#    init_post_marker_registration()
    return distance_to_cube(1)
#    return distance_to_marker(_left_post_marker_id)

def distance_to_right_post():
#    init_post_marker_registration()
    return distance_to_cube(2)
#    return distance_to_marker(_right_post_marker_id)

def align_ball_and_left_post():
#    init_post_marker_registration()
    return align_ball_and_cube(1)
#    return align_ball_and_marker(_left_post_marker_id)

def align_ball_and_right_post():
#    init_post_marker_registration()
    return align_ball_and_cube(2)
#    return align_ball_and_marker(_right_post_marker_id)


def align_with_ball_and_left_post():
    return align_ball_and_left_post()

def align_with_ball_and_right_post():
    return align_ball_and_right_post()

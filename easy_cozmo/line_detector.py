# -*- coding: utf-8 -*-

import asyncio
import cozmo
import cv2 as cv
import numpy as np
import math
import sys
from .line_detection_utils import pipeline, draw_lines, average_lines
from .defaults import *
from PIL import Image, ImageDraw, ImageFont
from . import easy_cozmo
from .movements import _move_head, move_lift_ground
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
from .robot_utils import pause

_line_detector = None
class LineAnnotator(cozmo.annotate.Annotator):
    def __init__(self, detector):
        super(LineAnnotator, self).__init__(detector._robot.world.image_annotator)
        self._detector = detector
    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        if self._detector.cline != None:
            scaled_line = [ x * scale for x in self._detector.cline]
            d.line(scaled_line, width=10, fill='green')
            draw_arrow = True
            if draw_arrow:
                px = scaled_line[0]
                py = scaled_line[1]
                angle = math.atan2(scaled_line[3] - scaled_line[1], scaled_line[2] - scaled_line[0])
                if angle < math.pi:
                    dangle = math.radians(30)
                    dx = math.cos(angle + dangle)
                    dy = math.sin(angle + dangle)
                    arrow_l = [px, py, px + 20*dx, py + 20*dy]
                    dx = math.cos(angle -dangle)
                    dy = math.sin(angle -dangle)
                    arrow_r = [px, py, px + 20*dx, py + 20*dy]
                    d.line(arrow_r, width=10, fill='green')
                    d.line(arrow_l, width=10, fill='green')

            #cv_im = draw_lines(cv_im, [[self._detector.cline]], thickness=100, color=[0,255,0])
        bounds = (0, 0, image.width, image.height)
        #batt = self.world.robot.battery_voltage
        if self._detector.signal is not None:
            text = None
            try:
                arialfont = ImageFont.truetype("arial.ttf", 28, encoding="unic")
                if arialfont != None:
                    text = cozmo.annotate.ImageText('ANGLE %d \u00b0 ' % self._detector.signal, font=arialfont, color='green')
            except:
                pass
            if text is None:
                text = cozmo.annotate.ImageText('ANGLE %d \u00b0 ' % self._detector.signal, color='green')
            text.render(d, bounds)


class LineDetector:
    def __init__(self, robot):
        self._robot = robot
        self._ma_lines = []
        self.cline = None
        self._robot.add_event_handler(cozmo.world.EvtNewCameraImage, self.on_img)
        self.anno = LineAnnotator(self)
        self._robot.world.image_annotator.add_annotator('houghlinedetect', self.anno)

        self.signal = 0

    def on_img(self, event, *, image:cozmo.world.CameraImage, **kw):
        raw_img = image.raw_image
        raw_rgb = np.array(raw_img)
        cv2_image = cv.cvtColor(raw_rgb, cv.COLOR_RGB2BGR)
        height, width, channels = cv2_image.shape
        args = {'rho': df_houghdetector_rho,
                'theta_div': df_houghdetector_thetadiv,
                'threshold': df_houghdetector_threshold,
                'minLineLength': df_houghdetector_minlinelength,
                'maxLineGap': df_houghdetector_maxlinegap,
                'lane_detection': df_houghdetector_lanedetection,
                'single_line_output': df_houghdetector_singlelineoutput,
                'draw_single_line':False,
                'draw_lines':False}
        lines, cv2_image = pipeline(cv2_image, **args)
        self._ma_lines += lines
        if len(self._ma_lines) > 10:
            self._ma_lines = self._ma_lines[-10:]
        self.cline = average_lines(self._ma_lines, cv2_image.shape[0])


        middleY = int(height * df_houghdetector_horizon)
        if self.cline:
            x1, y1, x2, y2 = self.cline
            dy = y2-y1
            dx = x2-x1
            self.signal = (math.degrees(math.atan2( dy,dx)) - 90)*-1
        else:
            self.signal = None

#        pil_img = image.raw_image
#        if self.cline is not None:
#            cv2_proc = draw_lines(cv2_image, [[self.cline]], thickness=10, color=[0,255,0])
#            cv2_proc=cv.circle(cv2_proc, (self.signal, middleY), 3, (0,0,255), -1) #Draw middle circle RED
#        raw_rgb = np.array(raw_img)

def init_line_detection():
    from .odometry import initialize_odometry
    initialize_line_detector()
    initialize_odometry()

def initialize_line_detector(algo='hough'):
    global _line_detector
    robot = easy_cozmo._robot
    if algo == 'hough':
        _line_detector = LineDetector(robot)

def get_detected_line_angle():
    if not _line_detector:
        print("WARNING: line detector not initialized, initializing ...")
        initialize_line_detector()

    # small pause to let the line detection thread processing some frames
    if abs(easy_cozmo._robot.head_angle.degrees - df_line_detection_head_angle) > 3:
        easy_cozmo._robot.set_head_angle(degrees(df_line_detection_head_angle)).wait_for_completed()
    #move_lift_ground()
    return _line_detector.signal

def is_line_detected():
    if not _line_detector:
        print("WARNING: line detector not initialized, initializing ...")
        initialize_line_detector()

    pause(0.05)
    return _line_detector.signal is not None

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 15:51:30 2018
Copyright Kinvert All Rights Reserved
If you would like to use this code for
business or education please contact
us for permission at:
www.kinvert.com/

@author: Keith
"""

import asyncio
import cozmo
import cv2 as cv
import numpy as np
import sys
from .line_detection_utils import pipeline, draw_lines, average_lines
from .mindcraft_defaults import *
from PIL import Image, ImageDraw


class LineAnnotator(cozmo.annotate.Annotator):
    def __init__(self, detector):
        super(LineAnnotator, self).__init__(detector._robot.world.image_annotator)
        self._detector = detector
    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        if self._detector.cline != None:
            print("drawing")
            print(self._detector.cline)
            scaled_line = [ x * scale for x in self._detector.cline]
            print(scaled_line)
            d.line(scaled_line, width=10, fill='green')
            #cv_im = draw_lines(cv_im, [[self._detector.cline]], thickness=100, color=[0,255,0])
        bounds = (0, 0, image.width, image.height)
        #batt = self.world.robot.battery_voltage
        text = cozmo.annotate.ImageText('SIGNAL %d' % self._detector.signal, color='green')
        text.render(d, bounds)


class LineDetector:
    def __init__(self, robot):
        self._robot = robot
        self._ma_lines = []
        self.cline = None
        self._robot.add_event_handler(cozmo.world.EvtNewCameraImage, self.on_img)
        self.anno = LineAnnotator(self)
        self._robot.world.image_annotator.add_annotator('houghlinedetect', self.anno)
        self._robot.world.image_annotator.add_static_text('text', 'Coz-Cam', position=cozmo.annotate.TOP_RIGHT)

        self.signal = 0
        
    def on_img(self, event, *, image:cozmo.world.CameraImage, **kw):   
        raw_img = image.raw_image
        raw_rgb = np.array(raw_img)
        cv2_image = cv.cvtColor(raw_rgb, cv.COLOR_RGB2BGR)
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

        middleY = 120
        if self.cline:
            x1, y1, x2, y2 = self.cline
            if abs(x2-x1) < 1:
                self.signal = x1
            else:
                m = 1.0*(y2-y1)/(x2-x1)
                b = y1 - m*x1
                self.signal = int((1.0*middleY - b)/m)
            print(self.signal)

#        pil_img = image.raw_image
#        if self.cline is not None:
#            cv2_proc = draw_lines(cv2_image, [[self.cline]], thickness=10, color=[0,255,0])
#            cv2_proc=cv.circle(cv2_proc, (self.signal, middleY), 3, (0,0,255), -1) #Draw middle circle RED
#        raw_rgb = np.array(raw_img)
        
 

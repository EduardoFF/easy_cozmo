#!/usr/bin/env python3

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
import math
import time
import sys
import asyncio
from cozmo.objects import CustomObject, LightCube

from .say import *
from .say import _say_error

from . import easy_cozmo
from .movements import *
import numpy as np

from .defaults import df_scan_object_speed,\
        df_use_headlight_for_scan_object,\
        df_move_relative_refined,\
        df_align_distance,\
        df_align_refined,\
        df_forget_old_when_scanning_objects, \
        df_reverse_speed, \
        df_use_distance_threshold_for_objects, \
        df_distance_threshold_for_objects

from .actions_with_objects import _get_visible_object, \
        _get_visible_objects, \
        _scan_for_object, \
        _move_relative_to_object, \
        _get_relative_pose, \
        _get_nearest_object, \
        _align_with_nearest_object

def _is_landmark(obj):
        return isinstance(obj, CustomObject) or isinstance(obj, LightCube)

def _get_visible_landmark():
        return _get_visible_object(_is_landmark, use_distance_threshold=False)

def _get_visible_landmarks():
        return _get_visible_objects(_is_landmark, use_distance_threshold=False)

def scan_for_landmark(angle, scan_speed=df_scan_object_speed):

        """**Rotate in place while looking for an object**

        This function executes a rotation, with certain angular speed
        and angle, while at the same time looking for an object.  As
        soon as Cozmo identifies a object in its field of view (not
        necessarily at the center of the camera), it stops.  As a
        result, Cozmo will keep seeing the object after it stops.

        :param angle: Angle to scan
        :type angle: float

            ..  note::

                If the angle is positive, Cozmo rotates in clockwise order. A negative angle is a counter clockwise rotation.

        :return: True (suceeded) or False (failed).
        """

        if not _scan_for_object(angle, valid_object_check=_is_landmark,
                                use_distance_threshold = False):
                return

        object = _get_visible_landmark()
        if not object:
                _say_error("I couldn't find a landmark, sorry")
                return False
        else:
                for i in range(3):
                        time.sleep(1)
                        if object.pose.origin_id != -1:
                                break
                if object.pose.origin_id == -1:
                        _say_error("I couldn't localize landmark, sorry")
                        return False

        return True


def double_scan_for_landmark(angle, scan_speed=df_scan_object_speed,
                         headlight_switching_enabled=True):

        """**Symmetric frontal scan for any object**

        A double scan is a more precise scanning procedure where Cozmo
        performs two passes with an aperture angle of 2*angle.  It
        ensures that each point within the angle is scanned twice.  If
        the head light is used (by default), it increases the chances
        that Cozmo will spot a object in front of it.

        :param angle: Angle to scan
        :type angle: float

        :return: True (suceeded) or False (failed)
        """
        if not _double_scan_for_object(angle=angle, scan_speed=scan_speed,
                                   valid_object_check=_is_landmark,
                                   headlight_switching_enabled = headlight_switching_enabled):
                _say_error("I couldn't find a landmark, sorry")
                return False


        landmark = _get_visible_landmark()
        if not landmark:
                _say_error("I can't see a landmark, sorry")
                return False
        else:
                """ ensure we get a landmark with valid pose """
                for i in range(3):
                        time.sleep(1)
                        if landmark.pose.origin_id != -1:
                                break
                if landmark.pose.origin_id == -1:
                        _say_error("I couldn't localize landmark, sorry")
                        return False

                return True

def _move_relative_to_landmark(landmark, pose, refined=df_move_relative_refined):
        return _move_relative_to_object(landmark, pose, refined)


def align_with_nearest_landmark(distance= df_align_distance,
                            refined = df_align_refined):
        """**Align with nearest object**

        Takes Cozmo toward the nearest object, and aligns to it

        :param distance: Desired distance between Cozmo and the object
        :type distance: float

        :return: True (suceeded) or False (failed) """
        return _align_with_nearest_object(distance, valid_object_check=_is_landmark, refined=refined, use_distance_threshold = False)

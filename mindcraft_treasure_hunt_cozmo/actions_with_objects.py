#!/usr/bin/env python3

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
import math
import time
import sys
import asyncio
from cozmo.objects import CustomObject

from .say import *
from .say import _say_error

from . import mindcraft
from .movements import *
import numpy as np

from .mindcraft_defaults import _df_scan_object_speed,\
        _df_use_headlight_for_scan_object,\
        _df_move_relative_refined,\
        _df_align_distance,\
        _df_align_refined,\
        _df_forget_old_when_scanning_objects, \
        _df_reverse_speed, \
        _df_use_distance_threshold_for_objects, \
        _df_distance_threshold_for_objects

def _get_visible_object():
        robot = mindcraft._mycozmo
        try:
                for visible_object in mindcraft._mycozmo.world.visible_objects:
                    if  isinstance(visible_object, cozmo.objects.CustomObject):
                            translation = robot.pose - visible_object.pose
                            dst = translation.position.x ** 2 + translation.position.y ** 2
                            dst = dst ** 0.5
                            if _df_use_distance_threshold_for_objects:
                                if dst > _df_distance_threshold_for_objects:
                                        continue

                            return visible_object
        except:
                pass
        return None

def _get_visible_objects():
        objects = []
        robot = mindcraft._mycozmo
        try:
                for visible_object in robot.world.visible_objects:
                    if  isinstance(visible_object, cozmo.objects.CustomObject):
                            translation = robot.pose - visible_object.pose
                            dst = translation.position.x ** 2 + translation.position.y ** 2
                            dst = dst ** 0.5
                            if _df_use_distance_threshold_for_objects:
                                if dst > _df_distance_threshold_for_objects:
                                        continue
                            objects.append(visible_object)
        except:
                pass
        return objects


def scan_for_object(angle, scan_speed=_df_scan_object_speed,
                        use_headlight=_df_use_headlight_for_scan_object):
        
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

        # makes positive angles cw 
        angle *= -1
        robot = mindcraft._mycozmo
        if _df_forget_old_when_scanning_objects:
                for obj in robot.world._objects.values():
                        obj.pose.invalidate()

        if use_headlight:
                robot.set_head_light(True)
        else:
                robot.set_head_light(False)
        
        action = robot.turn_in_place(degrees(angle), speed=scan_speed)
        while( not _get_visible_object()):
                if action.is_completed:
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
        object = _get_visible_object()
        if not object:
                _say_error("I couldn't find an object, sorry")
                return False
        else:
                for i in range(3):
                        time.sleep(1)
                        if object.pose.origin_id != -1:
                                break
                if object.pose.origin_id == -1:
                        _say_error("I couldn't localize object, sorry")
                        return False

        return True


def double_scan_for_object(angle, scan_speed=_df_scan_object_speed,
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
        robot = mindcraft._mycozmo
        if _df_forget_old_when_scanning_objects:
                for obj in robot.world._objects.values():
                        obj.pose.invalidate()

        scans=[degrees(angle),degrees(-2*angle),degrees(angle)]
        cnt_scan = 0
        head_light_enabled = False
        robot = mindcraft._mycozmo
        if headlight_switching_enabled:
                robot.set_head_light(head_light_enabled)
        action = robot.turn_in_place(scans[cnt_scan], speed=scan_speed)
        while( not _get_visible_object()):
                if action.is_completed:
                        head_light_enabled = not head_light_enabled
                        if headlight_switching_enabled:
                                robot.set_head_light(head_light_enabled)
                        cnt_scan += 1
                        if cnt_scan < len(scans):
                                action = robot.turn_in_place(scans[cnt_scan],speed=scan_speed)
                        else:
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
                say_error("Scan failed, sorry")
        object = _get_visible_object()
        if not object:
                _say_error("I couldn't see a object, sorry")
                if headlight_switching_enabled:
                        robot.set_head_light(head_light_enabled)
                return False
        else:
                for i in range(3):
                        time.sleep(1)
                        if object.pose.origin_id != -1:
                                break
                if object.pose.origin_id == -1:
                        _say_error("I saw a object, but I couldn't localize it, sorry")
                        if headlight_switching_enabled:
                                robot.set_head_light(head_light_enabled)
                        return False
        if headlight_switching_enabled:
                robot.set_head_light(head_light_enabled)
        return True

def _move_relative_to_object(object, pose, refined=_df_move_relative_refined):
        robot = mindcraft._mycozmo
        desired_pose_relative_to_object = pose
        object_pose_relative_to_robot = _get_relative_pose(object.pose, robot.pose)
        desired_pose_relative_to_robot = object_pose_relative_to_robot.define_pose_relative_this(desired_pose_relative_to_object)

        try:
                robot.go_to_pose(desired_pose_relative_to_robot, relative_to_robot=True,num_retries=3).wait_for_completed()
                if refined:
                        object_pose_relative_to_robot = _get_relative_pose(object.pose, robot.pose)
                        desired_pose_relative_to_robot = object_pose_relative_to_robot.define_pose_relative_this(
                        desired_pose_relative_to_object)
                        robot.go_to_pose(desired_pose_relative_to_robot, relative_to_robot=True,num_retries=3).wait_for_completed()
        except:
                say_error("Move action failed, sorry")
                return False
        return True


def _get_relative_pose(object_pose, reference_frame_pose):
        translation = np.matrix([[1, 0, 0, -reference_frame_pose.position.x],\
                                 [0, 1, 0, -reference_frame_pose.position.y],\
                                 [0, 0, 1, -reference_frame_pose.position.z],\
                                 [0, 0, 0, 1]])
        objectVector = np.matrix([[object_pose.position.x,\
                                   object_pose.position.y,\
                                   object_pose.position.z,\
                                   1]]).T
        originRotationRadians = -reference_frame_pose.rotation.angle_z.radians
        rotation = np.matrix([[math.cos(originRotationRadians), -math.sin(originRotationRadians), 0, 0], [math.sin(originRotationRadians), math.cos(originRotationRadians), 0, 0],
			[0, 0, 1, 0],
			[0, 0, 0, 1]])
        objectRelativeReference = (rotation * translation * objectVector).A1
        return cozmo.util.pose_z_angle(objectRelativeReference[0],
                                       objectRelativeReference[1],
                                       objectRelativeReference[2],
                                       cozmo.util.radians(object_pose.rotation.angle_z.radians + originRotationRadians))


def align_with_nearest_object(distance= _df_align_distance,
                            refined = _df_align_refined):
        """**Align with nearest object**

        Takes Cozmo toward the nearest object, and aligns to it

        :param distance: Desired distance between Cozmo and the object
        :type distance: float

        :return: True (suceeded) or False (failed) """
        robot = mindcraft._mycozmo           
        objects = _get_visible_objects()
        if len(objects)==0:
                _say_error("I can't align, I can't see any object")
                return False
        # find nearest one
        min_dst, targ = -1, None
        for object in objects:
                translation = robot.pose - object.pose
                dst = translation.position.x ** 2 + translation.position.y ** 2
                dst = dst ** 0.5
                if _df_use_distance_threshold_for_objects:
                        if dst > _df_distance_threshold_for_objects:
                                continue
                if min_dst < 0 or dst < min_dst:
                        min_dst, targ = dst, object

        if not targ:
                _say_error("I can't align, I can't see any nearby object")
                return False
        object = targ
        if object.pose.origin_id == -1:
                _say_error("I can't align, I can't localize the nearest object")
                return False
        heading = 0
        pose = Pose(-distance, 0, 0,
                    angle_z=radians(heading))
        print("Moving to relative pose ", pose)
        return _move_relative_to_object(object, pose, refined=refined)

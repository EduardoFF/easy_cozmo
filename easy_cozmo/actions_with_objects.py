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

_observable_objects = [cozmo.objects.CustomObject, cozmo.objects.LightCube]

def _is_observable_object(object):
        for object_type in _observable_objects:
                if  isinstance(object, object_type):
                        return True
        return False

def _get_visible_object(valid_object_check=_is_observable_object,
                        use_distance_threshold = df_use_distance_threshold_for_objects):
        robot = easy_cozmo._robot
        try:
                for visible_object in easy_cozmo._robot.world.visible_objects:
                    if  valid_object_check(visible_object):
                            if visible_object.pose.origin_id == -1:
                                continue
                            translation = robot.pose - visible_object.pose
                            dst = translation.position.x ** 2 + translation.position.y ** 2
                            dst = dst ** 0.5
                            if use_distance_threshold:
                                if dst > df_distance_threshold_for_objects:
                                        continue

                            return visible_object
        except:
                pass
        return None

def _get_visible_objects(valid_object_check=_is_observable_object,
                         use_distance_threshold = df_use_distance_threshold_for_objects):
        objects = []
        robot = easy_cozmo._robot
        try:
                for visible_object in robot.world.visible_objects:
                    if  valid_object_check(visible_object):
                            translation = robot.pose - visible_object.pose
                            dst = translation.position.x ** 2 + translation.position.y ** 2
                            dst = dst ** 0.5
                            if use_distance_threshold:
                                if dst > df_distance_threshold_for_objects:
                                        continue
                            objects.append(visible_object)
        except:
                pass
        return objects

def _wait_for_visible_objects(valid_object_check=_is_observable_object, use_distance_threshold = df_use_distance_threshold_for_objects):
        objects = []
        robot = easy_cozmo._robot
        try:
                for i in range(5):
                        for visible_object in robot.world.visible_objects:
                            if  valid_object_check(visible_object):
                                    translation = robot.pose - visible_object.pose
                                    dst = translation.position.x ** 2 + translation.position.y ** 2
                                    dst = dst ** 0.5
                                    if use_distance_threshold:
                                        if dst > df_distance_threshold_for_objects:
                                                continue
                                    objects.append(visible_object)
                        time.sleep(.2)
        except:
                pass
        return objects


def _scan_for_object(angle, scan_speed=df_scan_object_speed,
                     valid_object_check=_is_observable_object,
                     use_distance_threshold = df_use_distance_threshold_for_objects):

        """**Rotate in place while looking for an observable object**

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
        robot = easy_cozmo._robot
        if df_forget_old_when_scanning_objects:
                for obj in robot.world._objects.values():
                        if valid_object_check(obj):
                                obj.pose.invalidate()

        action = robot.turn_in_place(degrees(angle), speed=degrees(scan_speed))
        while( not _get_visible_object(valid_object_check, use_distance_threshold = use_distance_threshold)):

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
        object = _get_visible_object(valid_object_check, use_distance_threshold = use_distance_threshold)
        if not object:
                return False
        else:
                for i in range(3):
                        time.sleep(1)
                        if object.pose.origin_id != -1:
                                break
                if object.pose.origin_id == -1:
                        return False

        #print("Found object ", object)
        return True


def _double_scan_for_object(angle, scan_speed=df_scan_object_speed,
                            valid_object_check = _is_observable_object,
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
        robot = easy_cozmo._robot
        if df_forget_old_when_scanning_objects:
                for obj in robot.world._objects.values():
                        obj.pose.invalidate()

        scans=[degrees(angle),degrees(-2*angle),degrees(angle)]
        cnt_scan = 0
        head_light_enabled = False
        robot = easy_cozmo._robot
        if headlight_switching_enabled:
                robot.set_head_light(head_light_enabled)
        action = robot.turn_in_place(scans[cnt_scan], speed=degrees(scan_speed))
        while( not _get_visible_object(valid_object_check)):
                if action.is_completed:
                        head_light_enabled = not head_light_enabled
                        if headlight_switching_enabled:
                                robot.set_head_light(head_light_enabled)
                        cnt_scan += 1
                        if cnt_scan < len(scans):
                                action = robot.turn_in_place(scans[cnt_scan],speed=degrees(scan_speed))
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
        object = _get_visible_object(valid_object_check)
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

def _move_relative_to_object(object, pose, refined=df_move_relative_refined):
        robot = easy_cozmo._robot
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
                _say_error("Move action failed, sorry")
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


def _get_nearest_object(valid_object_check=_is_observable_object,
                        use_distance_threshold = df_use_distance_threshold_for_objects):
        robot = easy_cozmo._robot
        objects = _wait_for_visible_objects(valid_object_check,
                                            use_distance_threshold=use_distance_threshold)
        if len(objects)==0:
                #print("I can't align, I can't see any object")
                return False
        # find nearest one
        min_dst, targ = -1, None
        for object in objects:
                if object.pose.origin_id == -1:
                        continue
                translation = robot.pose - object.pose
                dst = translation.position.x ** 2 + translation.position.y ** 2
                dst = dst ** 0.5
                if use_distance_threshold:
                        if dst > df_distance_threshold_for_objects:
                                continue
                if min_dst < 0 or dst < min_dst:
                        min_dst, targ = dst, object

        if not targ:
                #print("I can't align, I can't see any nearby object")
                return False
        object = targ
        if object.pose.origin_id == -1:
                #print("I can't align, I can't localize the nearest object")
                return False
        #print("Found nearest object ",object)
        return object

def _align_with_nearest_object(distance= df_align_distance,
                              valid_object_check=_is_observable_object,
                               refined = df_align_refined,
                               use_distance_threshold = df_use_distance_threshold_for_objects):
        """**Align with nearest object**

        Takes Cozmo toward the nearest object, and aligns to it

        :param distance: Desired distance between Cozmo and the object
        :type distance: float

        :return: True (suceeded) or False (failed) """
        object = _get_nearest_object(valid_object_check,
                                     use_distance_threshold = use_distance_threshold)
        if not object:
                return

        # handle special case of cubes that considers nearest face
        if isinstance(object, LightCube):
                from .actions_with_cubes import _align_with_cube
                return _align_with_cube(object, distance=distance, refined=refined)


        heading = 0
        pose = Pose(-distance, 0, 0,
                    angle_z=radians(heading))
        return _move_relative_to_object(object, pose, refined=refined)


def _align_with_object(obj, distance= df_align_distance,
                       valid_object_check=_is_observable_object,
                       refined = df_align_refined,
                       use_distance_threshold = df_use_distance_threshold_for_objects):
        """**Align with nearest object**

        Takes Cozmo toward the nearest object, and aligns to it

        :param distance: Desired distance between Cozmo and the object
        :type distance: float

        :return: True (suceeded) or False (failed) """
        if not obj:
                return
        robot = easy_cozmo._robot
        if obj.pose.origin_id == -1:
                _say_error("Object is not localized")
                return
        translation = robot.pose - obj.pose
        dst = translation.position.x ** 2 + translation.position.y ** 2
        dst = dst ** 0.5
        if use_distance_threshold:
                if dst > df_distance_threshold_for_objects:
                        _say_error("Object is too far")

        # handle special case of cubes that considers nearest face
        if isinstance(obj, LightCube):
                from .actions_with_cubes import _align_with_cube
                return _align_with_cube(obj, distance=distance, refined=refined)


        heading = 0
        pose = Pose(-distance, 0, 0,
                    angle_z=radians(heading))
        return _move_relative_to_object(obj, pose, refined=refined)

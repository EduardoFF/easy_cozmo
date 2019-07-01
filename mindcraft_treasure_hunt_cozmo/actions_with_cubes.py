#!/usr/bin/env python3

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
import math
import time
import sys
import asyncio
from cozmo.objects import LightCubeIDs, LightCube

from .say import *
from .say import _say_error

from . import easy_cozmo
from .movements import *
from .movements import _execute_go_to_pose
import numpy as np

from .defaults import df_scan_cube_speed,\
        df_use_headlight_for_scan_cube,\
        df_move_relative_refined,\
        df_align_distance,\
        df_align_refined,\
        df_forget_old_when_scanning_cubes, \
        df_pickup_retries, \
        df_reverse_speed, \
        df_use_distance_threshold_for_cubes, \
        df_distance_threshold_for_cubes

from .actions_with_objects import _get_visible_object, \
        _get_visible_objects, \
        _scan_for_object, \
        _move_relative_to_object, \
        _get_relative_pose, \
        _get_nearest_object

def _get_visible_cube_by_id(cube_id):
        def check_cube_id(obj):
                return _is_cube(obj) and obj.cube_id == cube_id
        cube = _get_visible_object(valid_object_check=check_cube_id)
        if not cube:
                return False
        return cube

def _cube_one():
        return get_visible_cube_by_id(robot, 1)

def _cube_two():
        return get_visible_cube_by_id(robot, 2)

def _cube_three():
        return get_visible_cube_by_id(robot, 2)

def _is_cube(obj):
        return obj is not None and isinstance(obj, LightCube)

def _get_visible_cube():
        return _get_visible_object(_is_cube)

def _get_visible_cubes():
        return _get_visible_objects(_is_cube)

def scan_for_cube(angle, scan_speed=df_scan_cube_speed):

        """**Rotate in place while looking for any cube**

        This function executes a rotation, with certain angular speed
        and angle, while at the same time looking for a specific cube
        defined by its id.  As soon as Cozmo identifies a cube in its
        field of view (not necessarily at the center of the camera),
        it stops. As a result, Cozmo will keep seeing the cube after
        it stops.

        :param angle: Angle to scan
        :type angle: float

        .. note::
            If the angle is positive, Cozmo rotates in clockwise order. A negative angle is a counter clockwise rotation.

        :return: True (suceeded) or False (failed).

        """

        if not _scan_for_object(angle, valid_object_check=_is_cube, scan_speed=scan_speed):
                _say_error("I couldn't find a cube, sorry")
                return False
        cube = _get_visible_cube()
        if not cube:
                _say_error("I can't see a cube, sorry")
                return False
        else:
                """ ensure we get a cube with valid pose """
                for i in range(3):
                        time.sleep(1)
                        if cube.pose.origin_id != -1:
                                break
                if cube.pose.origin_id == -1:
                        _say_error("I couldn't localize cube, sorry")
                        return False

        return True


def scan_for_cube_by_id(angle, cube_id, scan_speed=df_scan_cube_speed):

        """**Rotate in place while looking for a cube with specified id**

        This function executes a rotation, with certain angular speed
        and angle, while at the same time looking for a specific cube
        defined by its id.  As soon as Cozmo identifies a cube in its
        field of view (not necessarily at the center of the camera),
        it stops. As a result, Cozmo will keep seeing the cube after
        it stops.

        :param angle: Angle to scan
        :type angle: float
        :param cube_id: Id of the cube to be picked up, either 1, 2, or 3. If the cube id is wrong, Cozmo will complain with a sound.
        :type cube_id: int

        .. note::
            If the angle is positive, Cozmo rotates in clockwise order. A negative angle is a counter clockwise rotation.

        :return: True (suceeded) or False (failed).

        """

        def check_cube_id(obj):
                return _is_cube(obj) and obj.cube_id == cube_id
        if _scan_for_object(angle, scan_speed, valid_object_check=check_cube_id):
                cube = _get_visible_cube_by_id(cube_id)
                if not cube:
                        _say_error("I can't see cube "+str(cube_id) +" sorry")
                        return False
                else:
                        for i in range(3):
                                time.sleep(1)
                                if cube.pose.origin_id != -1:
                                        break
                        if cube.pose.origin_id == -1:
                                _say_error("I can't localize cube "+str(cube_id) +" sorry")
                                return False
        else:
                _say_error("I couldn't find cube ", cube_id)
                return False


        return True


def scan_for_cube_one(angle, scan_speed=df_scan_cube_speed):
        """**Scan for cube with id=1**

        Same as scan_for_cube_by_id(3)

        :param angle: Angle to scan
        :type angle: float

        :return: True (suceeded) or False (failed)

        """

        return scan_for_cube_by_id(angle, 1, scan_speed)
def scan_for_cube_two(angle, scan_speed=df_scan_cube_speed):
        """**Scan for cube with id=1**

        Same as scan_for_cube_by_id(3)

        :param angle: Angle to scan
        :type angle: float

        :return: True (suceeded) or False (failed)

        """
        return scan_for_cube_by_id(angle, 2, scan_speed)

def scan_for_cube_three(angle, scan_speed=df_scan_cube_speed):

        """**Scan for cube with id=1**

        Same as scan_for_cube_by_id(3)

        :param angle: Angle to scan
        :type angle: float

        :return: True (suceeded) or False (failed)

        """
        return scan_for_cube_by_id(angle, 3, scan_speed)

def double_scan_for_any_cube(angle, scan_speed=df_scan_cube_speed,
                         headlight_switching_enabled=True):

        """**Symmetric frontal scan for any cube**

        A double scan is a more precise scanning procedure where Cozmo
        performs two passes with an aperture angle of 2*angle.  It
        ensures that each point within the angle is scanned twice.  If
        the head light is used (by default), it increases the chances
        that Cozmo will spot a cube in front of it.

        :param angle: Angle to scan
        :type angle: float

        :return: True (suceeded) or False (failed)
        """
        if not _double_scan_for_object(angle=angle, scan_speed=scan_speed,
                                   valid_object_check=_is_cube,
                                   headlight_switching_enabled = headlight_switching_enabled):
                _say_error("I couldn't find a cube, sorry")
                return False


        cube = _get_visible_cube()
        if not cube:
                _say_error("I can't see a cube, sorry")
                return False
        else:
                """ ensure we get a cube with valid pose """
                for i in range(3):
                        time.sleep(1)
                        if cube.pose.origin_id != -1:
                                break
                if cube.pose.origin_id == -1:
                        _say_error("I couldn't localize cube, sorry")
                        return False

                return True

def _move_relative_to_cube(cube, pose, refined=df_move_relative_refined):
       return  _move_relative_to_object(cube, pose, refined)

def _find_nearest_face(cube):
        import math
        robot = easy_cozmo._robot
        cube_pose1_relative_to_robot = _get_relative_pose(cube.pose, robot.pose)
        #print("relative pose1 ", cube_pose1_relative_to_robot)
        cube_pose2_relative_to_robot = robot.pose.define_pose_relative_this(cube.pose)
        #print("relative pose2 ", cube_pose2_relative_to_robot)
        pose = cube_pose1_relative_to_robot
        x_axis = math.cos(pose.rotation.angle_z.radians)
        y_axis = math.cos(pose.rotation.angle_z.radians+math.pi*0.5)
        if abs(x_axis) > abs(y_axis):
                return ((1 if x_axis>=0 else -1),0,0)
        else:
                return (0,(1 if y_axis>=0 else -1),0)

def _align_with_cube(cube, distance=df_align_distance, refined=df_align_refined):
        if not cube:
                return False
        if not isinstance(cube, LightCube):
                return False
        nearest_face = _find_nearest_face(cube)
        #print("Aligning with cube's nearest face ", nearest_face)
        heading = math.atan2(nearest_face[1], nearest_face[0])
        pose = Pose(-distance*nearest_face[0], -distance*nearest_face[1], 0,
                    angle_z=radians(heading))
        #print("Moving to relative pose ", pose)
        return _move_relative_to_cube(cube, pose, refined=refined)

def align_with_nearest_cube(distance= df_align_distance,
                            refined = df_align_refined):
        """**Align with nearest cube**

        Takes Cozmo toward the nearest cube, and aligns it to the
        cube's nearest face.

        :param distance: Desired distance between Cozmo and the cube
        :type distance: float

        :return: True (suceeded) or False (failed) """
        cube = _get_nearest_object(_is_cube)
        return _align_with_cube(cube)


def pickup_cube():
        """ """
        easy_cozmo._robot.set_head_angle(degrees(0)).wait_for_completed()
        easy_cozmo._robot.set_head_light(False)
        cube = _get_visible_cube()
        if cube is None:
                _say_error("I can't see cube ", cube_id)
                return False
        return _pickup_visible_cube(cube)


def _pickup_visible_cube(cube):
        if not _is_cube(cube):
                _say_error("Invalid cube ")
                return False
        action=None
        try:
                action=easy_cozmo._robot.pickup_object(cube, num_retries=df_pickup_retries)
                action.wait_for_completed()
                if action.has_failed:
                        code, reason = action.failure_reason
                        result = action.result
                        print("WARNING: PickupCube: code=%s reason='%s' result=%s" % (code, reason, result))
                        _say_error("I couldn't pickup the cube ", cube.cube_id,
                                   " sorry")
                        action.abort()
                        return False
                else:
                        return True
        except Exception as e:
                import traceback
                print(e)
                traceback.print_exc()
        _say_error("I couldn't pickup cube ", cube.cube_id, " sorry")
        return False

def pickup_cube_by_id(cube_id):
        """**Pick up the cube with specified id**

        This function executes a pickup action that involves the following
        sequence of step.
        - Moving Cozmo's head to straight position. We assume that the cube
        lies on the same place as Cozmo.
        - Setting the head light off. Note that the head light helps Cozmo
        seeing cubes at medium/far distances, while it is not good at close
        distances.
        - Checking that a cube with the indicated id is visible. Note that it
        does not attempt to search for it. Cozmo must be able to see the
        cube in its current position. If Cozmo cannot see the cube, it may
        complain with a message.
        - Doing the pickup action using the lift. Note that Cozmo does it best
        to pickup the cube, but sometimes it fails. When it fails, it may
        detect the failure and apologize for the incovenience. In a few
        cases, it could wrongly believe that it suceeded when it actually
        failed. Be patient and give Cozmo another chance.

        :param cube_id: Id of the cube to be picked up, either 1, 2, or 3. If the cube id is wrong, Cozmo will complain with a sound.
        :type cube_id: int
        :return: True (suceeded) or False (failed) according to what Cozmo believes it happened.
        """

        from .actions_with_cubes import _get_visible_cube_by_id
        if cube_id not in [1,2,3]:
                say_error("Cube id " + str(cube_id) + " not good")
                return False
        easy_cozmo._robot.set_head_angle(degrees(0)).wait_for_completed()
        easy_cozmo._robot.set_head_light(False)
        cube = _get_visible_cube_by_id(cube_id)
        if cube is None:
                _say_error("I can't see cube ", cube_id)
                return False
        return _pickup_visible_cube(cube)


def pickup_cube_one():
        """**Pick up cube with id=1**

        Same as pickup_by_cube_id(1)

        :return: True (suceeded) or False (failed) according to what Cozmo thinks is the result.

        """
        return pickup_cube_by_id(1)


def pickup_cube_two():
        """**Pick up cube with id=2**

        Same as pickup_by_cube_id(2)

        :return: True (suceeded) or False (failed) according to what Cozmo thinks is the result.

        """
        return pickup_cube_by_id(2)


def pickup_cube_three():
        """**Pick up cube with id=3**

        Same as pickup_by_cube_id(3)

        :return: True (suceeded) or False (failed) according to what Cozmo thinks is the result.

        """
        return pickup_cube_by_id(3)

def drop_cube():
        """**Drop a cube in the current location**

        This function involves a sequence of two actions.

        - Moving the lift to the ground
        - Moving in reverse for two seconds (which takes Cozmo approximately 10 centimeters behind the cube

        :return: True if the cube could be dropped, or False if an error occurred.

        """

        move_lift_ground()
        reverse_in_seconds(2)

def place_on_top(cube_id):
        from .actions_with_cubes import _get_visible_cube_by_id
        if cube_id not in [1,2,3]:
                say_error("Cube id " + str(cube_id) + " not good")
                return False
        easy_cozmo._robot.set_head_angle(degrees(0)).wait_for_completed()
        easy_cozmo._robot.set_head_light(False)
        cube = _get_visible_cube_by_id(cube_id)
        if not cube:
                _say_error("I can't see cube ", cube_id)
                return False
        action=None
        try:
                action=easy_cozmo._robot.place_on_object(cube, num_retries=df_pickup_retries)
                action.wait_for_completed()
                if action.has_failed:
                        code, reason = current_action.failure_reason
                        result = current_action.result
                        print("WARNING: PlaceOnObject: code=%s reason='%s' result=%s" % (code, reason, result))
                        _say_error("I couldn't place the cube ", cube_id, " sorry")
                        action.abort()
                        return False
                else:
                        return True
        except:
                pass
        _say_error("I couldn't place the cube ", cube_id, " sorry")
        return False

def place_on_top_of_one():
        return place_on_top(1)
def place_on_top_of_two():
        return place_on_top(2)
def place_on_top_of_three():
        return place_on_top(3)

def center_cube(cube_id):
        robot = easy_cozmo._robot
        if cube_id not in [1,2,3]:
                say_error("Cube id " + str(cube_id) + " not good")
                return False
        robot.set_head_angle(degrees(0)).wait_for_completed()
        robot.set_head_light(False)
        cube = _get_visible_cube_by_id(cube_id)
        if cube is None:
                _say_error("I can't see cube ", cube_id)
                return False
        cube = _get_visible_cube_by_id(cube_id)
        if cube is None:
                _say_error("I can't see cube ", cube_id)
                return False
        rel_pose = _get_relative_pose(cube.pose, robot.pose)
        print("RELATIVE POSE ", rel_pose)
        cube_pose = (rel_pose.position.x, rel_pose.position.y)
        print("CUBE POSE ", cube_pose)
        angle = math.atan2(cube_pose[1], cube_pose[0])
        print("Angle = ", angle)
        pose = Pose(0, 0, 0, angle_z=radians(angle))
        ret = _execute_go_to_pose(pose)
        return ret

def distance_to_cube(cube_id):
        robot = easy_cozmo._robot
        if cube_id not in [1,2,3]:
                say_error("Cube id " + str(cube_id) + " not good")
                return False
        cube = _get_visible_cube_by_id(cube_id)
        if not cube:
                _say_error("I can't see cube ", cube_id)
                return False
        translation = robot.pose - cube.pose
        dst = translation.position.x ** 2 + translation.position.y ** 2
        dst = dst ** 0.5
        return dst

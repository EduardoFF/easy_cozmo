#!/usr/bin/env python3

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
import math
import time
import sys
import asyncio
from cozmo.objects import LightCubeIDs

from .say import *
from . import mindcraft
from .movements import *
import numpy as np

from .mindcraft_defaults import _df_scan_cube_speed,\
        _df_use_headlight_for_scan_cube,\
        _df_move_relative_refined,\
        _df_align_distance,\
        _df_align_refined,\
        _df_forget_old_when_scanning_cubes, \
        _df_pickup_retries, \
        _df_reverse_speed

def _get_visible_cube_by_id(cube_id):
        ignore_list = set([1,2,3])
        if cube_id is None or cube_id not in ignore_list:
                return False
        ignore_list.remove(cube_id)
        ignore_list = list(ignore_list)
        cube = _get_visible_cube(ignore_list)
        if not cube:
                return False
        return cube

def _cube_one():
        return get_visible_cube_by_id(robot, 1)
        
def _cube_two():
        return get_visible_cube_by_id(robot, 2)

def _cube_three():
        return get_visible_cube_by_id(robot, 2)


def _get_visible_cube(ignore_list=None):
        try:
                for visible_object in mindcraft._mycozmo.world.visible_objects:
                    if  isinstance(visible_object, cozmo.objects.LightCube):
                            if ignore_list is None or visible_object.cube_id not in ignore_list:
                                    return visible_object
        except:
                pass
        return None

def scan_for_cube_by_id(angle, cube_id, scan_speed=_df_scan_cube_speed,
                        use_headlight=_df_use_headlight_for_scan_cube):
        
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

        # makes positive angles cw 
        angle *= -1
        robot = mindcraft._mycozmo
        if _df_forget_old_when_scanning_cubes:
                for obj in robot.world._objects.values():
                        obj.pose.invalidate()

        if use_headlight:
                robot.set_head_light(True)
        else:
                robot.set_head_light(False)
        
        action = robot.turn_in_place(degrees(angle), speed=scan_speed)
        while( not _get_visible_cube_by_id(cube_id)):
                if action.is_completed:
                        break
        try:
                while action.is_running:
                        action.abort()
                        time.sleep(.5)
                                
        except Exception as e:
                import traceback
                print(e)
                traceback.print_exc()
                say_error("Scan faulty")
        cube = _get_visible_cube_by_id(cube_id)
        if not cube:
                say_error("Scan for cube "+str(cube_id) +" failed")
                return False
        else:
                for i in range(3):
                        time.sleep(1)
                        if cube.pose.origin_id != -1:
                                break
                if cube.pose.origin_id == -1:
                        say_error("Scan for cube "+str(cube_id) +" failed, can't locate cube")
                        return False

        return True


def scan_for_cube_one(angle, scan_speed=_df_scan_cube_speed,
                       use_headlight=_df_use_headlight_for_scan_cube):
        """**Scan for cube with id=1** 
        
        Same as scan_for_cube_by_id(3)

        :param angle: Angle to scan 
        :type angle: float 

        :return: True (suceeded) or False (failed)

        """

        return scan_for_cube_by_id(angle, 1, scan_speed, use_headlight)
def scan_for_cube_two(angle, scan_speed=_df_scan_cube_speed,
                       use_headlight=_df_use_headlight_for_scan_cube):
        """**Scan for cube with id=1** 
        
        Same as scan_for_cube_by_id(3)

        :param angle: Angle to scan 
        :type angle: float 

        :return: True (suceeded) or False (failed)

        """
        return scan_for_cube_by_id(angle, 2, scan_speed, use_headlight)

def scan_for_cube_three(angle, scan_speed=_df_scan_cube_speed,
                        use_headlight=_df_use_headlight_for_scan_cube):
        
        """**Scan for cube with id=1** 
        
        Same as scan_for_cube_by_id(3)

        :param angle: Angle to scan 
        :type angle: float 

        :return: True (suceeded) or False (failed)

        """
        return scan_for_cube_by_id(angle, 3, scan_speed, use_headlight)

def double_scan_for_any_cube(angle, scan_speed=_df_scan_cube_speed,
                         headlight_switching_enabled=True, ignore_list=None):

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
        robot = mindcraft._mycozmo
        if _df_forget_old_when_scanning_cubes:
                for obj in robot.world._objects.values():
                        obj.pose.invalidate()

        scans=[degrees(angle),degrees(-2*angle),degrees(angle)]
        cnt_scan = 0
        head_light_enabled = False
        robot = mindcraft._mycozmo
        if headlight_switching_enabled:
                robot.set_head_light(head_light_enabled)
        action = robot.turn_in_place(scans[cnt_scan], speed=scan_speed)
        while( not _get_visible_cube(ignore_list)):
                if action.is_completed:
                        head_light_enabled = not head_light_enabled
                        if headlight_switching_enabled:
                                robot.set_head_light(head_light_enabled)
                        cnt_scan += 1
                        if cnt_scan < len(scans):
                                action = robot.turn_in_place(scans[cnt_scan],speed=scan_speed)
                        else:
                                break
        try:
                while action.is_running:
                        action.abort()
                        time.sleep(.5)
        except Exception as e:
                import traceback
                print(e)
                traceback.print_exc()
                say_error("Scan failed, sorry")
        cube = _get_visible_cube()
        if not cube:
                say_error("Scan for cube  failed")
                if headlight_switching_enabled:
                        robot.set_head_light(head_light_enabled)
                return False
        else:
                for i in range(3):
                        time.sleep(1)
                        if cube.pose.origin_id != -1:
                                break
                if cube.pose.origin_id == -1:
                        say_error("Scan failed, can't localize cube")
                        if headlight_switching_enabled:
                                robot.set_head_light(head_light_enabled)
                        return False
        if headlight_switching_enabled:
                robot.set_head_light(head_light_enabled)
        return True

def _move_relative_to_cube(cube, pose, refined=_df_move_relative_refined):
        robot = mindcraft._mycozmo
        desired_pose_relative_to_cube = pose
        cube_pose_relative_to_robot = _get_relative_pose(cube.pose, robot.pose)
        desired_pose_relative_to_robot = cube_pose_relative_to_robot.define_pose_relative_this(desired_pose_relative_to_cube)

        try:
                robot.go_to_pose(desired_pose_relative_to_robot, relative_to_robot=True,num_retries=3).wait_for_completed()
                if refined:
                        cube_pose_relative_to_robot = _get_relative_pose(cube.pose, robot.pose)
                        desired_pose_relative_to_robot = cube_pose_relative_to_robot.define_pose_relative_this(
                        desired_pose_relative_to_cube)
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

def _find_nearest_face(cube):
        import math
        robot = mindcraft._mycozmo
        cube_pose1_relative_to_robot = _get_relative_pose(cube.pose, robot.pose)
        print("relative pose1 ", cube_pose1_relative_to_robot)
        cube_pose2_relative_to_robot = robot.pose.define_pose_relative_this(cube.pose)
        print("relative pose2 ", cube_pose2_relative_to_robot)
        pose = cube_pose1_relative_to_robot
        x_axis = math.cos(pose.rotation.angle_z.radians)
        y_axis = math.cos(pose.rotation.angle_z.radians+math.pi*0.5)
        if abs(x_axis) > abs(y_axis):
                return ((1 if x_axis>=0 else -1),0,0)
        else:
                return (0,(1 if y_axis>=0 else -1),0)

def align_with_nearest_cube(distance= _df_align_distance,
                            refined = _df_align_refined):
        """**Align with nearest cube**

        Takes Cozmo toward the nearest cube, and aligns it to the
        cube's nearest face. 

        :param distance: Desired distance between Cozmo and the cube
        :type distance: float

        :return: True (suceeded) or False (failed) """
           
        cube = _get_visible_cube()
        if cube is None or not cube:
                say_error("Can't align, I can't see any cube")
                return False
        if cube.pose.origin_id == -1:
                say_error("Can't align, I can't localize cube")
        nearest_face = _find_nearest_face(cube)
        print("nearest face ", nearest_face)
        heading = math.atan2(nearest_face[1], nearest_face[0])
        pose = Pose(-distance*nearest_face[0], -distance*nearest_face[1], 0,
                    angle_z=radians(heading))
        print("moving to relative pose ", pose)
        return _move_relative_to_cube(cube, pose, refined=refined)

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
                say_error("Cube id not good")
                return False
        mindcraft._mycozmo.set_head_angle(degrees(0)).wait_for_completed()
        mindcraft._mycozmo.set_head_light(False)
        cube = _get_visible_cube_by_id(cube_id)
#        robot.abort_all_actions()
        if not cube:
                return False
        action=None
        try:
                action=mindcraft._mycozmo.pickup_object(cube, num_retries=_df_pickup_retries)
                action.wait_for_completed()
                if action.has_failed:
                        code, reason = current_action.failure_reason
                        result = current_action.result
                        print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
                        say_error("Couldn't pickup, sorry")
                        action.abort()
                        return False
                else:
                        return True
        except:
                pass
        say_error("Couldn't pickup, sorry")
        return False

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
 

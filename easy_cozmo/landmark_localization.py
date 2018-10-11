# -*- coding: utf-8 -*-
"""
Created on October 8, 2018

A very basic localization strategy based on fixed landmarks

@author: Eduardo

"""

import asyncio
import cozmo
import math
import sys
from .mindcraft_defaults import *
from . import mindcraft
from .movements import move_head_looking_up, move_head_looking_forward, _move_head
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
from math import pi, sqrt, sin, cos, atan2, exp
import time
from .actions_with_objects import _get_visible_object, \
        _get_visible_objects, \
        _scan_for_object, \
        _move_relative_to_object, \
        _get_relative_pose, \
        _get_nearest_object
from .odometry import *
from .actions_with_objects import _get_relative_pose

""" a map from _CustomObjectType to (x,y) """
_loc_landmarks={}
_loc_landmarks_origin={}
_loc_odom_origin = Pose(0,0,0, angle_z = radians(0))
_loc_locating = False
_loc_heading = False
_loc_heading_to = None

def initialize_landmark_localization():
    global _loc_landmarks, _loc_pose, _loc_locating, _loc_heading, _loc_landmarks_origin
    _loc_odom_origin = Pose(0,0,0, angle_z = radians(0))
    reset_odometry()
    _loc_locating = False
    _loc_heading = False
    robot = mindcraft._mycozmo
    robot.world.undefine_all_custom_marker_objects()
    mindcraft._mycozmo.world.define_custom_wall(CustomObjectTypes.CustomType01,
                                                CustomObjectMarkers.Circles3,
                                                180, 180, 180, 180, True)

    mindcraft._mycozmo.world.define_custom_wall(CustomObjectTypes.CustomType02,
                                                CustomObjectMarkers.Diamonds2,
                                                180, 180, 180, 180, True)

    _loc_landmarks = {CustomObjectTypes.CustomType01: Pose(0,0,0, angle_z = degrees(0)), CustomObjectTypes.CustomType02: Pose(0,0,0, angle_z = degrees(0)) }

    _loc_landmarks_origin = {CustomObjectTypes.CustomType01: Pose(0,0,0, angle_z = degrees(0)), CustomObjectTypes.CustomType02: Pose(1200,0,0, angle_z = degrees(180)) }
    

    robot.add_event_handler(cozmo.objects.EvtObjectObserved,
                            on_obj_observed)
    

""" NORTH is CustomType01 """

def north():
    return CustomObjectTypes.CustomType01

def south():
    return CustomObjectTypes.CustomType02


def distance_to_north():
    return distance_to('N')

def distance_to_south():
    return distance_to('S')

def distance_to(to):
    robot = mindcraft._mycozmo
    landmark_pose = None
    if to == 'N':
        landmark_pose = _loc_landmarks[north()]
    elif to == 'S':
        landmark_pose = _loc_landmarks[south()]
    else:
        return None
        
    translation = robot.pose - landmark_pose
    dst = translation.position.x ** 2 + translation.position.y ** 2
    dst = dst ** 0.5
    return dst/10.


def head_north():
    return _head_to('N')

def head_south():
    return _head_to('S')

def _head_to(to):
    global _loc_heading_to, _loc_heading
    angle = 360
    scan_speed= 20
    robot = mindcraft._mycozmo
    _move_head(degrees(15))    
    action = robot.turn_in_place(degrees(angle), speed=degrees(scan_speed))
    _loc_heading_to = to
    _loc_heading = True

    while( _loc_heading ):
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
    ok = not _loc_heading
    _loc_heading = False
    return ok

def is_centered_in_cam(p):
    return p[0] >= 140 and p[0] <= 180

def _localize_with(obj):
    global _loc_odom_origin
    robot = mindcraft._mycozmo
    lpose = _loc_landmarks[obj]
    print("landmark ", obj, " @ ", lpose)
    rel_pose = _get_relative_pose(robot.pose, lpose)
    print("robot relative pose wrt landmark ", rel_pose)
    _loc_odom_origin = _loc_landmarks_origin[obj] + rel_pose
    print("new odom origin ", _loc_odom_origin)
    
    reset_odometry(_loc_odom_origin)
    

def on_obj_observed(evt, **kw):
    global _loc_heading, _loc_locating
    #if not _loc_locating and not _loc_heading:
    #    return
    robot = mindcraft._mycozmo
    if isinstance(evt.obj, CustomObject):
        print("Cozmo started seeing a %s" % str(evt.obj.object_type))
#        print("Imagebox ", str(evt.image_box))
        if _is_loc_landmark(evt.obj):
            translation = robot.pose - evt.pose
            dst = translation.position.x ** 2 + translation.position.y ** 2
            dst = dst ** 0.5
            _loc_landmarks[evt.obj.object_type] = evt.pose
            _localize_with(evt.obj.object_type)
            print("set pose ", evt.pose)
            if _loc_heading:
                if _loc_heading_to == 'N' and evt.obj.object_type == north():
                    if is_centered_in_cam(evt.image_box.center):
                        _loc_heading = False
                elif _loc_heading_to=='S' and evt.obj.object_type == south():
                    if is_centered_in_cam(evt.image_box.center):
                        _loc_heading = False


            #print("Is location landmark @ distance ", dst, " mm")
            

def _is_loc_landmark(obj):
    return isinstance(obj, CustomObject) and obj.object_type in _loc_landmarks

def where_am_i():
    global _loc_locating
    forget_when_locating = True
    angle = 360
    scan_speed = 20
    _move_head(degrees(15))    
    #move_head_looking_forward()
    """ do a full rotation while watching for landmarks """    
    robot = mindcraft._mycozmo
    if forget_when_locating:
            for obj in robot.world._objects.values():
                    if _is_loc_landmark(obj):
                            obj.pose.invalidate()

    _loc_locating = True
    try:
        action = robot.turn_in_place(degrees(angle), speed=degrees(scan_speed)).wait_for_completed()                                
    except Exception as e:
            import traceback
            print(e)
            traceback.print_exc()
    _loc_locating = False

def _valid_pose(pose):
    return pose is not None and pose.origin_id != -1

def get_heading_angle():
    # use only north

    robot = mindcraft._mycozmo
    lpose = _loc_landmarks[north()]
    if _valid_pose(lpose):
        rel_pose = _get_relative_pose(robot.pose, lpose)
        return rel_pose.rotation.angle_z
    else:
        return None

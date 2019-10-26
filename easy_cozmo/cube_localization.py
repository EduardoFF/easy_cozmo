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
from .defaults import *
from . import easy_cozmo
from .movements import move_head_looking_up, move_head_looking_forward, _move_head
from cozmo.util import degrees, Angle, Pose, distance_mm, radians
from cozmo.objects import CustomObject, LightCube, CustomObjectTypes, CustomObjectMarkers
from cozmo.objects import LightCube
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
_loc_cubes={}
_loc_cubes_origin={}
_loc_odom_origin = Pose(0,0,0, angle_z = radians(0))
_loc_locating = False
_loc_heading = False
_loc_heading_to = None

def initialize_cube_localization():
    global _loc_cubes, _loc_pose, _loc_locating, _loc_heading, _loc_cubes_origin
    _loc_odom_origin = Pose(0,0,0, angle_z = radians(0))
    reset_odometry()
    _loc_locating = False
    _loc_heading = False
    robot = easy_cozmo._robot
    robot.world.undefine_all_custom_marker_objects()
    robot.world.define_custom_box(CustomObjectTypes.CustomType01,
                                   CustomObjectMarkers.Circles4,  # front
                                   CustomObjectMarkers.Hexagons3,   # back
                                   CustomObjectMarkers.Diamonds3,   # top
                                   CustomObjectMarkers.Diamonds2,   # bottom
                                   CustomObjectMarkers.Circles2, # left
                                   CustomObjectMarkers.Diamonds5, # right
                                   65,65,65,
                                   62, 62, True)

    robot.world.define_custom_box(CustomObjectTypes.CustomType02,
                                   CustomObjectMarkers.Circles3,  # front
                                   CustomObjectMarkers.Hexagons5,   # back
                                   CustomObjectMarkers.Circles5,   # top
                                   CustomObjectMarkers.Triangles4,   # bottom
                                   CustomObjectMarkers.Triangles2, # left
                                   CustomObjectMarkers.Diamonds4, # right
                                   65, 65, 65,
                                   62, 62, True)

    _loc_cubes = {1: Pose(-120,200,0, angle_z = degrees(0)), \
                  2: Pose(0,540,0, angle_z = degrees(0)), \
                  3: Pose(120,880,0, angle_z = degrees(0)), \
                  CustomObjectTypes.CustomType01: Pose(0,0,0,angle_z=degrees(0)),\
                  CustomObjectTypes.CustomType02: Pose(0,0,0,angle_z=degrees(0))}

    _loc_cubes_origin = {1: Pose(-440,480,0, angle_z = degrees(0)), \
                         2: Pose(440,480,0, angle_z = degrees(0)), \
                         3: Pose(-440,1000,0, angle_z = degrees(0)),
                         CustomObjectTypes.CustomType01: Pose(0,700,0,angle_z=degrees(0)),\
                          CustomObjectTypes.CustomType02: Pose(440,1000,0,angle_z=degrees(0))}


    initialize_odometry()
    robot.add_event_handler(cozmo.objects.EvtObjectObserved,
                            on_obj_observed)




def distance_to(to):
    robot = easy_cozmo._robot
    cube_pose = _loc_cubes[to]

    translation = robot.pose - cube_pose
    dst = translation.position.x ** 2 + translation.position.y ** 2
    dst = dst ** 0.5
    return dst/10.


def _localize_with(cube_id):
    global _loc_odom_origin
    robot = easy_cozmo._robot
    lpose = _loc_cubes[cube_id]
#    print("cube ", cube_id, " @ ", lpose)
    rel_pose = _get_relative_pose(robot.pose, lpose)
#    print("robot relative pose wrt cube ", rel_pose)
    _loc_odom_origin = _loc_cubes_origin[cube_id] + rel_pose
#    print("new odom origin ", _loc_odom_origin)
    reset_odometry(_loc_odom_origin)


def loc_id(obj):
    if isinstance(obj, LightCube):
        return obj.cube_id
    else:
        if isinstance(obj, CustomObject):
            return obj.object_type
    return None

def on_obj_observed(evt, **kw):
    global _loc_heading, _loc_locating
    #if not _loc_locating and not _loc_heading:
    #    return
    robot = easy_cozmo._robot
    if _is_loc_cube(evt.obj):
        translation = robot.pose - evt.pose
        dst = translation.position.x ** 2 + translation.position.y ** 2
        dst = dst ** 0.5
        lid = loc_id(evt.obj)
        _loc_cubes[lid] = evt.pose
        if evt.pose.is_accurate:
            _localize_with(lid)
            #print("set pose ", evt.pose)


            #print("Is location cube @ distance ", dst, " mm")


def _is_loc_cube(obj):
    if isinstance(obj, LightCube) and obj.cube_id in _loc_cubes:
        return True
    else:
        if isinstance(obj, CustomObject) and obj.object_type in _loc_cubes:
            return True
    return False

def where_am_i():
    global _loc_locating
    forget_when_locating = True
    angle = 360
    scan_speed = 20
    _move_head(degrees(15))
    #move_head_looking_forward()
    """ do a full rotation while watching for cubes """
    robot = easy_cozmo._robot
    if forget_when_locating:
            for obj in robot.world._objects.values():
                    if _is_loc_cube(obj):
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
    pass

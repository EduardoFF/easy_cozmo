# -*- coding: utf-8 -*-
"""
Created on October 4th, 2018

@author: Eduardo
"""

import asyncio
import cozmo
import math
import sys
from .defaults import *
from . import easy_cozmo

from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians, pose_z_angle
from math import pi, sqrt, sin, cos, atan2, exp
from .comm import *

_traveled_distance = 0
_heading_offset = 0
_odom_pose = Pose(0,0,0, angle_z = degrees(0))
last_odom_pose = None
_odom_origin = Pose(0,0,0, angle_z = degrees(0))

def wrap_angle(angle_rads):
    """Keep angle between -pi and pi."""
    if angle_rads <= -pi:
        return 2*pi + angle_rads
    elif angle_rads > pi:
        return angle_rads - 2*pi
    else:
        return angle_rads

def on_motion(event, *, robot: cozmo.robot.Robot , **kw):
    global last_odom_pose, _traveled_distance, _heading_offset, _odom_pose

    if robot.are_wheels_moving:
        # How much did we move since last evaluation?
        if last_odom_pose is None:
            last_odom_pose = robot.pose
            return
        if  robot.pose.is_comparable(last_odom_pose):
            dx = robot.pose.position.x - last_odom_pose.position.x
            dy = robot.pose.position.y - last_odom_pose.position.y
            dist = sqrt(dx*dx + dy*dy)
       #     _odom_pose += pose_z_angle(dx, dy, 0, radians(turn_angle))
            turn_angle = wrap_angle( robot.pose.rotation.angle_z.radians - last_odom_pose.rotation.angle_z.radians)
            #print("odom_pose ", _odom_pose)
            _odom_pose = _odom_pose.define_pose_relative_this(pose_z_angle(dist, 0, 0, radians(0)))
            _odom_pose = _odom_pose.define_pose_relative_this(pose_z_angle(0, 0, 0, radians(turn_angle)))
            notify_pose()

        else:
            dist = 0
            turn_angle = 0
            print('** Robot origin_id changed from', last_odom_pose.origin_id,
                  'to', robot.pose.origin_id)

        last_odom_pose = robot.pose
        _traveled_distance += dist
        _heading_offset = wrap_angle(_heading_offset + turn_angle)

def initialize_odometry():
    global _traveled_distance, _heading_offset
    initialize_comm()

    _traveled_distance = 0
    _heading_offset =  0
    reset_odometry()
    mindcraft._mycozmo.add_event_handler(cozmo.robot.EvtRobotStateUpdated,
                                         on_motion)

def set_odom_origin(x, y):
    global _odom_origin
    _odom_origin = Pose(x*10, y*10, 0, angle_z = degrees(0))

def reset_odometry(pose = None):
    global _traveled_distance, _heading_offset, _odom_pose
    if pose is None:
        _odom_pose = _odom_origin
    else:
        _odom_pose = pose
    notify_pose()
    _traveled_distance = 0
    _heading_offset = 0

def notify_pose():
    x = int(_odom_pose.position.x)
    y = int(_odom_pose.position.y)
    theta = float(_odom_pose.rotation.angle_z.radians)

    send("cozmo/pose", "%d %d %.2f"%(int(x),int(y),theta))


def get_distance_traveled():
    return _traveled_distance/10.

def get_odom_pose():
    return _odom_pose

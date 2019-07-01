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
_traveled_distance = 0
last_odom_pose = None
odom_pose = pose_z_angle(0,0,0,degrees(0))

def wrap_angle(angle_rads):
    """Keep angle between -pi and pi."""
    if angle_rads <= -pi:
        return 2*pi + angle_rads
    elif angle_rads > pi:
        return angle_rads - 2*pi
    else:
        return angle_rads

def on_motion(event, *, robot: cozmo.robot.Robot , **kw):
    global last_odom_pose, _traveled_distance, _odom_pose
    if robot.are_wheels_moving:
        # How much did we move since last evaluation?
        if last_odom_pose is None:
            last_odom_pose = robot.pose
            return
        if  robot.pose.is_comparable(last_odom_pose):
            dx = robot.pose.position.x - last_odom_pose.position.x
            dy = robot.pose.position.y - last_odom_pose.position.y
            dist = sqrt(dx*dx + dy*dy)
            turn_angle = wrap_angle(robot.pose.rotation.angle_z.radians -
                                    last_odom_pose.rotation.angle_z.radians)
            _odom_pose += pose_z_angle(dx, dy, 0, radians(turn_angle))
        else:
            dist = 0
            turn_angle = 0
            print('** Robot origin_id changed from', last_odom_pose.origin_id,
                  'to', robot.pose.origin_id)

        last_odom_pose = robot.pose
        _traveled_distance += dist

def initialize_odometry():
    global _traveled_distance, _odom_pose
    _traveled_distance = 0
    _odom_pose = pose_z_angle(0,0,0,degrees(0))
    easy_cozmo._robot.add_event_handler(cozmo.robot.EvtRobotStateUpdated,
                                         on_motion)
def reset_odometry():
    global _traveled_distance, _odom_pose
    _traveled_distance = 0
    _odom_pose = pose_z_angle(0,0,0,radians(0))

def get_distance_traveled():
    return _traveled_distance/10.

def get_odom_pose():
    return _odom_pose

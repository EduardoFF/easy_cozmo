#!/usr/bin/env python3

import asyncio
import time
import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
from .mindcraft_defaults import _df_scan_face_speed
from . import mindcraft
from .say import *
from .movements import *

def is_any_teammate_visible():
        return _get_visible_teammate_face() is not False
        
""" returns a face object """
def _get_visible_teammate_face(ignore_list=[]):
        robot = mindcraft._mycozmo
        try:
                for visible_face in robot.world.visible_faces:
                    if visible_face.name != '':
                        if ignore_list is None or visible_face.name not in ignore_list:
                                    return visible_face
        except:
                pass
        return False
""" returns a string """
def _get_visible_teammate_name():
        teammate = _get_visible_teammate_face()
        if not teammate:
                return ""
        return teammate.name

def scan_for_any_teammate(angle=360,scan_speed=_df_scan_face_speed, ignore_list=None):
        """**Rotate in place while looking for a teammate**

        This function executes a rotation, with certain angular speed
        and angle, while at the same time looking for any face
        previously registered using the Meet Cozmo App.  As soon as
        Cozmo identifies a registered face in its field of view (not
        necessarily at the center of the camera), it stops the
        rotation.  As a result, Cozmo should keep seeing the cube
        after it stops.

        :param angle: Angle to scan
        :type angle: float

        ..  note::

          If the angle is positive, Cozmo rotates in clockwise order. A negative angle is a counter clockwise rotation.

        :return: True (suceeded) or False (failed).
        """
        robot = mindcraft._mycozmo
        print("going to start looking for familiar faces")
        action = robot.turn_in_place(degrees(angle), speed=scan_speed)
        print("started first action ")
        while( not _get_visible_teammate_face(ignore_list=ignore_list) ):
                if action.is_completed:
                    break
        try:
                if action.is_running:
                        action.abort()
                        while action.is_running:
                                pass
        except:
                say_error("Scan faulty")
        if action.is_running:
                action.abort()
                while action.is_running:
                        pass


        face = _get_visible_teammate_face(ignore_list)
        if not face:
                say_error("Oh I can't find any teammate")
                return False
        return True
    

def say_something_to_visible_teammate( text_before='', text_after='', *args):
        """**Identify a visible teammate, and say something mentioning
        the teammate's name**

        This action comprises a sequence of three steps.

            - Aligning Cozmo toward a visible teammate

            - Identifying the teammate by checking the record of
              familiar faces

            - Constructing a sentence that mentions the name of
              teammate

            - Using Cozmo's speech synthesis capabilities to say the
              sentence.

        :param text_before: Text to be said BEFORE the name
        :type text_before: string

        :param text_after: Text to be said AFTER the name
        :type text_after: string

        ..  note::

                This function receives a variable number or arguments.
                All arguments will be concatenated and delimited by a
                space, and appended at the end of the message. This is useful to
                compose sentences.

        :return: True (suceeded) or False (failed)
        """
        
        if not _align_with_any_visible_teammate(once=True):
                say_error("I can't see any teammate")
                return False
                
        name = _get_visible_teammate_name()
        if name == "":
                say_error("Oh I can't identify teammate. Sorry")
                return False
        
        text_after = text_after + ' '.join(map(str, args))

        mindcraft._mycozmo.say_text(text_before+name+text_after).wait_for_completed()
        return True

def enable_facial_expression_recognition():
        """**Enable facial expresion recognition to identify mood**
        """
        mindcraft._mycozmo.enable_facial_expression_estimation(enable=True)
        
def disable_facial_expression_recognition():
        """**Disable facial expresion recognition**
        """

        mindcraft._mycozmo.enable_facial_expression_estimation(enable=False)

def _is_happy_face(robot, face, timeout=False):
        """****
        """
        start_time = time.time()
        from cozmo.faces import FACIAL_EXPRESSION_HAPPY
        if face is None:
                return False
        if timeout:
                while True:
                        if face.known_expression == FACIAL_EXPRESSION_HAPPY:
                                return True
                        if time.time() - start_time > timeout:
                                break
        return face.known_expression == FACIAL_EXPRESSION_HAPPY

def _align_with_any_visible_teammate(once=False):
        face_to_follow = None
        robot = mindcraft._mycozmo

        while True:
                turn_action = None
                if face_to_follow:
                        # start turning towards the face
                        turn_action = robot.turn_towards_face(face_to_follow)

                if not (face_to_follow and face_to_follow.is_visible):
                        # find a visible face,
                        # timeout if nothing found after a short while
                        try:
                                face_to_follow = robot.world.wait_for_observed_face(timeout=5)
                        except asyncio.TimeoutError:
                                return False

                if turn_action:
                        # Complete the turn action if one was in progress
                        try:
                                turn_action.wait_for_completed()
                        except:
                                return False
                        if once:
                                break
        return True
            
def align_with_any_visible_teammate():
        """**Align with any visible teammate**

        Align Cozmo's body with a visible teammate.  As a result, the
        face will appear centered in Cozmo's camera.

        :return: True (suceeded) or False (failed)

        .. note::
           This action is useful to control Cozmo's heading angle using your face.
        """

        return _align_with_any_visible_teammate(once=True)
    

#!/usr/bin/env python3

import asyncio
import time
import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
from .defaults import df_scan_face_speed
from . import easy_cozmo
from .say import *
from .say import _say_error
from .movements import *

def is_teammate_visible():
        return _get_visible_teammate_face() is not False
def is_face_visible():
        return _get_visible_face(only_named=False)

""" returns a face object """

def _get_visible_face(only_named=False):
        robot = easy_cozmo._robot
        try:
                for visible_face in robot.world.visible_faces:
                        if only_named:
                                if visible_face.name != '':
                                        return visible_face
                        else:
                                return visible_face
        except:
                pass
        return False

def _get_visible_teammate_face():
        return _get_visible_face(only_named=True)


""" returns a string """
def _get_visible_teammate_name():
        teammate = _get_visible_face(only_named=True)
        if not teammate:
                return ""
        return teammate.name

def _scan_for_faces(angle=360, scan_speed=df_scan_face_speed, only_named=False):
        """**Rotate in place while looking for teammates**

        This function executes a rotation, with certain angular speed
        and angle, while at the same time looking for any face
        previously registered using the Meet Cozmo App.  As soon as
        Cozmo identifies a registered face in its field of view (not
        necessarily at the center of the camera), it stops the
        rotation.  As a result, Cozmo should keep seeing the cube
        after it stops.

        :param angle: Angle to scan (in degrees)
        :type angle: float

        ..  note::

          If the angle is positive, Cozmo rotates in clockwise order. A negative angle is a counter clockwise rotation.

        :return: True (suceeded) or False (failed)
        """
        robot = easy_cozmo._robot
        # makes positive angles cw
        angle *= -1

        action = robot.turn_in_place(degrees(angle), speed=degrees(scan_speed))
        #print("started first action ")
        while( not _get_visible_face(only_named=only_named) ):
                if action.is_completed:
                        break
                time.sleep(.25)
        try:
                if action.is_running:
                        action.abort()
                        while action.is_running:
                                action.abort()
                                time.sleep(.5)

        except Exception as e:
                import traceback
                print(e)
                traceback.print_exc()
                say_error("Scan faulty")
        if action.is_running:
                action.abort()
                while action.is_running:
                        action.abort()
                        sleep(.5)


        face = _get_visible_face(only_named=only_named)
        if not face:
                _say_error("I can't find a face, sorry")
                return False
        return True

def scan_for_teammates(angle=360, scan_speed=df_scan_face_speed):
        return _scan_for_faces(angle, scan_speed, only_named=True)


def scan_for_faces(angle=360,scan_speed=df_scan_face_speed):
        """**Rotate in place while looking for any human faces**

        This function executes a rotation, with certain angular speed
        and angle, while at the same time looking for any face
        previously registered using the Meet Cozmo App.  As soon as
        Cozmo identifies a human face (not necessarily registered) in
        its field of view (not necessarily at the center of the
        camera), it stops the rotation.  As a result, Cozmo should
        keep seeing the cube after it stops.

        :param angle: Angle to scan (in degrees)
        :type angle: float

            ..  note::

                If the angle is positive, Cozmo rotates in clockwise order. A negative angle is a counter clockwise rotation.

        :return: True (suceeded) or False (failed)
        """
        return _scan_for_faces(angle, scan_speed, only_named=False)



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

        if not _align_with_visible_face(once=True):
                _say_error("I can't see any teammate, sorry")
                return False

        name = _get_visible_teammate_name()
        if name == "":
                _say_error("I can't identify teammate, sorry")
                return False

        text_after = text_after + ' '.join(map(str, args))

        easy_cozmo._robot.say_text(text_before+" "+name+" "+text_after).wait_for_completed()
        return True

def enable_facial_expression_recognition():
        """**Enable facial expresion recognition to identify mood**
        """
        easy_cozmo._robot.enable_facial_expression_estimation(enable=True)

def disable_facial_expression_recognition():
        """**Disable facial expresion recognition**
        """

        easy_cozmo._robot.enable_facial_expression_estimation(enable=False)

def wait_for_a_smiling_face_visible(timeout=False):
        """**Look for a smiling expression**

        :param timeout: amount of time, in seconds, to wait for a smiling face. If zero, false, or None, no waiting time is used and instant check is done

        :type timeout: int

        """
        enable_facial_expression_recognition()
        start_time = time.time()
        from cozmo.faces import FACIAL_EXPRESSION_HAPPY
        retval = False
        if timeout:
                while not retval:
                        face = _get_visible_face()
                        if face and  face.known_expression == FACIAL_EXPRESSION_HAPPY:
                                retval = True
                                break
                        if time.time() - start_time > timeout:
                                break
                        time.sleep(.2)
        face = _get_visible_face()
        if face:
                retval |= face.known_expression == FACIAL_EXPRESSION_HAPPY
        disable_facial_expression_recognition()

        return retval


def _align_with_visible_face(once=False):
        face_to_follow = None
        robot = easy_cozmo._robot

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
                time.sleep(.2)
        return True


def align_with_face():
        """**Align with any visible face**

        Align Cozmo's body with a visible teammate.  As a result, the
        face will appear centered in Cozmo's camera.

        :return: True (suceeded) or False (failed)

        .. note::
           This action is useful to control Cozmo's heading angle using your face.
        """

        return _align_with_visible_face(once=True)

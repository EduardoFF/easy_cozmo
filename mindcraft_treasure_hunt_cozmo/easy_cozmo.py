import asyncio
import time
import cozmo

"""
module globals
_user_program: function (any type)
_robot: cozmo.robot.Robot
"""

_robot = None
using_viewer = True
from .initialize_robot import initialize_robot
from .defaults import df_image_stream_enabled
def _easy_cozmo_main(robot: cozmo.robot.Robot):
    global _robot
    _robot = robot
    initialize_robot(_robot)
    _robot.camera.image_stream_enabled = using_viewer
    print("Robot initialized ", _robot)
    _user_program()


def run_program(program):
    """**Run a program in Cozmo**

    This is the entry point for a Cozmo program. Under the hood, it
    sets up the communication link with your Cozmo, initilizes the
    robot, and executes your code on it.

    :param program: The code that you want to execute on Cozmo
    :type program: python function

    """
    global _user_program
    global using_viewer
    _user_program = program
    using_viewer = False
    cozmo.run_program(_easy_cozmo_main, use_viewer=False)

def run_program_with_viewer(program):
    """**Run a program in Cozmo in debug mode and launch the viewer
    to display what Cozmo sees**

    This is the entry point for a Cozmo program.  Under the hood, it
    sets up the communication link with your Cozmo, initializes the
    robot, and executes your code on it.

    :param program: The code that you want to execute on Cozmo
    :type program: python function
    """

    global _user_program
    global df_image_stream_enabled
    _user_program = program
    df_image_stream_enabled = True
    cozmo.run_program(_easy_cozmo_main, use_viewer=True)

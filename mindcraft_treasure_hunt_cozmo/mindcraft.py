import asyncio
import time
import cozmo

""" 
module globals
_user_program: function (any type) 
_mycozmo: cozmo.robot.Robot
"""

_mycozmo = None
from .initialize_robot import initialize_robot
    
def _mindcraft_main(robot: cozmo.robot.Robot):
    global _mycozmo
    _mycozmo = robot
    initialize_robot(_mycozmo)
    print("Robot initialized ", _mycozmo)
    _user_program()


def run_on_cozmo(program):
    """**Runs a program in Cozmo and launchs the viewer to display what
    Cozmo sees**

    This is the entry point for a Cozmo program. Under the hood, it
    sets up the communication link with your Cozmo, initilizes the
    robot, and executes your code on it.

    :param program: The code that you want to execute on Cozmo
    :type program: python function
    
    """
    global _user_program
    _user_program = program
    cozmo.run_program(_mindcraft_main, use_viewer=False)

def run_on_cozmo_debug_mode(program):
    """**Run a program in Cozmo in debug mode and launch the viewer
    to display what Cozmo sees**

    This is the entry point for a Cozmo program.  Under the hood, it
    sets up the communication link with your Cozmo, initializes the
    robot, and executes your code on it.

    :param program: The code that you want to execute on Cozmo
    :type program: python function
    """
    from .mindcraft_defaults import _df_image_stream_enabled
    global _user_program
    _user_program = program
    _df_image_stream_enabled = True
    cozmo.run_program(_mindcraft_main, use_viewer=True)

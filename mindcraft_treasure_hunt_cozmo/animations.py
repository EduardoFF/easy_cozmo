import cozmo
from . import easy_cozmo
from .say import _say_error, say_error


def show_happy():
    try:
        easy_cozmo._robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabHappy).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_victory():
    try:
        easy_cozmo._robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabExcited).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_excited():
    try:
        easy_cozmo._robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabFireTruck).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_sad():
    try:
        easy_cozmo._robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabLose).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_frustrated():
    try:
        easy_cozmo._robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabFrustrated).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_dancing():
    try:
        easy_cozmo._robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabDancingMambo).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

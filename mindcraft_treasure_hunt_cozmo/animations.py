import cozmo
from . import mindcraft
from .say import _say_error, say_error


def show_happy():
    try:
        mindcraft._mycozmo.play_anim_trigger(cozmo.anim.Triggers.CodeLabHappy).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_victory():
    try:
        mindcraft._mycozmo.play_anim_trigger(cozmo.anim.Triggers.CodeLabExcited).wait_for_completed()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_excited():
    try:
        mindcraft._mycozmo.play_anim_trigger(cozmo.anim.Triggers.CodeLabFireTruck).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_sad():
    try:
        mindcraft._mycozmo.play_anim_trigger(cozmo.anim.Triggers.CodeLabLose).wait_for_completed()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")
    
def show_frustrated():
    try:
        mindcraft._mycozmo.play_anim_trigger(cozmo.anim.Triggers.CodeLabFrustrated).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")

def show_dancing():
    try:
        mindcraft._mycozmo.play_anim_trigger(cozmo.anim.Triggers.CodeLabDancingMambo).wait_for_completed()
    except:
        import traceback
        traceback.print_exc()
        print(e)
        say_error("Animation failed")


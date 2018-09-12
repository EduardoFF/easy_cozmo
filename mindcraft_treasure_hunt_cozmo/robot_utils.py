import time
from . import mindcraft

def pause(time_in_seconds):
    """**Pause for certain amount of time in seconds**
    
    :param time_in_seconds: time to pause
    :type time_in_seconds: float
    """
    time.sleep(time_in_seconds)
    
def abort():
    """**Abort the entire program execution**
    """
    print("Aborting program...")
    raise SystemExit
def enable_head_light():
    mindcraft._mycozmo.set_head_light(True)
def disable_head_light():
    mindcraft._mycozmo.set_head_light(False)


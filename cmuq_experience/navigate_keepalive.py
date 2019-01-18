from robot_tools import *
import time
from kbhit import KBHit
import mindcraft_treasure_hunt_cozmo.mindcraft as mc
from PIL import Image, ImageDraw, ImageFont

kb = None
msg="IDLE"

class TourAnnotator(cozmo.annotate.Annotator):
    def __init__(self):
        super(TourAnnotator, self).__init__(mc._mycozmo.world.image_annotator)
    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        bounds = (0, 0, image.width, image.height)
        text = None
        try:
            arialfont = ImageFont.truetype("arial.ttf", 14, encoding="unic")
            if arialfont != None:
                text = cozmo.annotate.ImageText('%s ' % msg, font=arialfont, color='green')
        except:
            pass
        if text is None:
            text = cozmo.annotate.ImageText('%s ' % msg, color='green')
        text.render(d, bounds)


def start_tour():
    global msg
    robot = mc._mycozmo
    n = read_tour('tour.txt')
    pause(1)
    initialize_nav()
    msg = "Tour %s, PRESS s or S to START, ESC to cancel"%(tour_str())
    while True:
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27: # ESC
                return
            if ord(c) == 115 or ord(c) == 83:
                msg = "STARTED"
                print("GO!!!!")
                break
    current_loc = 1
    start_time = time.time()
    while current_loc <= n:
        msg = "Going to %d"%(loc(current_loc))
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27: # ESC
                robot.abort_all_actions()
                return
        navigate_to2(current_loc)
        while navigating():
            if risk_of_collision():
                pause_navigation()
                resume_navigation()
            if kb.kbhit():
                c = kb.getch()
                if ord(c) == 27: # ESC
                    robot.abort_all_actions()
                    return
        if navigation_successful():
            say("", loc(current_loc))
            #collect_reward(current_loc)
            current_loc = current_loc + 1
        else:
            error("Trying again")
    elapsed_time = time.time() - start_time
    say("task completed")
    msg = "COMPLETED! TOTAL_TIME %d seconds PRESS ESC to RESET"%(elapsed_time)
    print("ELAPSED TIME ", elapsed_time)
    celebrate()
    while True:
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27: # ESC
                return

def cozmo_program():
    global kb, msg
    read_locations('locations_final.txt')
    n = read_tour('tour.txt')
    initialize()
    touranno = TourAnnotator()
    robot = mc._mycozmo
    robot.world.image_annotator.add_annotator('touranno', touranno)
    kb = KBHit()
    msg="Update tour and PRESS s or S to start tour"
    while True:
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 115 or ord(c)==83: # s or S
                start_tour()
                msg="Update tour and PRESS s or S to start tour"
        time.sleep(0.5)

    kb.set_normal_term()



run_program_with_viewer(cozmo_program)

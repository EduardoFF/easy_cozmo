from robot_tools import *
import time
from kbhit import KBHit
import mindcraft_treasure_hunt_cozmo.mindcraft as mc
from PIL import Image, ImageDraw, ImageFont
import sys

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
    print(msg)
    while True:
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27: # ESC
                return
            elif ord(c) == 115 or ord(c) == 83:
                msg = "STARTED"
                print(msg)
                break
            else:
                msg = "Tour %s, PRESS s or S to START, ESC to cancel"%(tour_str())
                print(msg)
        time.sleep(0.5)
    current_loc = 1
    start_time = time.time()
    while current_loc <= n:
        msg = "Going to %d"%(loc(current_loc))
        print(msg)
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
    print(msg)
    celebrate()
    while True:
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27: # ESC
                return
            else:
                msg = "PRESS ESC to RESET"
                print(msg)
        time.sleep(0.5)

def cozmo_program():
    global kb, msg
    read_locations('locations_final.txt')
    n = read_tour('tour.txt')
    initialize()
    touranno = TourAnnotator()
    robot = mc._mycozmo
    robot.world.image_annotator.add_annotator('touranno', touranno)
    kb = KBHit()
    msg="Update tour and PRESS s or S to start tour, x to EXIT"
    print(msg)
    while True:
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 115 or ord(c)==83: # s or S
                start_tour()
                msg="Update tour and PRESS s or S to start tour, x to EXIT"
                print(msg)
            if ord(c) == 88 or ord(c) == 120:
                msg="Are you sure you want to exit? y/n"
                print(msg)
                confirm_exit = False
                while True:
                    if kb.kbhit():
                        c = kb.getch()
                        if ord(c) == 121 or ord(c)==89: # y or Y
                            confirm_exit = True
                            break
                        elif ord(c) == 78 or ord(c) == 110:
                            break
                        else:
                            msg="Please enter y or n"
                            print(msg)
                    time.sleep(0.5)
                if confirm_exit:
                    break
        time.sleep(0.5)

    kb.set_normal_term()

if __name__ == "__main__":
    video_enabled = True
    for arg in sys.argv:
        if arg == 'novideo' or arg == '--no-video' or arg == '-novideo':
            video_enabled = False
            print("novid")

    if video_enabled:
        run_program_with_viewer(cozmo_program)
    else:
        run_program(cozmo_program)

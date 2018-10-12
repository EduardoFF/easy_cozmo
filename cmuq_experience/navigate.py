from robot_tools import *
import time
    
def cozmo_program():
    read_locations('locations_final.txt')
    n = read_tour('tour.txt')
    initialize()    
    current_loc = 1
    pause(3)
    start_time = time.time()
    while current_loc <= n:
        navigate_to2(current_loc)
        while navigating():
            if risk_of_collision():
                pause_navigation()
                resume_navigation()
        if navigation_successful():
            say("Arrived to ", loc(current_loc))
            collect_reward(current_loc)
            current_loc = current_loc + 1
        else:
            error("Trying again")
    elapsed_time = time.time() - start_time
    say("task completed")
    print("ELAPSED TIME ", elapsed_time)
    celebrate()

run_program_with_viewer(cozmo_program)

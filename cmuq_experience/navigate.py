from robot_tools import *

    
def cozmo_program():
    read_locations('locations_final.txt')
    n = read_tour('tour.txt')
    initialize()    
    current_loc = 1
    while current_loc <= n:
        navigate_to(current_loc)
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
    say("task completed")
    celebrate()

run_program_with_viewer(cozmo_program)

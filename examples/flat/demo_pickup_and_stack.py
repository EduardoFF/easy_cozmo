"""
Task: Cozmo picks cube number one up and places it on top of cube number two
"""
say("Searching for cube one")
move_head_looking_forward()

# we use variable "completed" to check if the robot could successfully
# stack the cubes up
completed = False

if scan_for_cube_one(360):
    say("Picking up cube one")
    if pickup_cube_one():
        move_lift_up()
        move_head_looking_forward()
        say("Searching for cube two")
        if scan_for_cube_two(360):
            say("Placing cube one on top of cube two")
            if place_on_top(2):
                completed = True    
            else:
                say("Sorry, I couldn't place the cube")
        else:
            say("I couldn't find the cube")
    else:
        say("Sorry, I couldn't pick the cube")
else:
    say("Sorry, I couldn't find the cube")

if completed:
    say("Completed the task")
    show_dancing()
else:
    say("Failed the task")
    show_sad()


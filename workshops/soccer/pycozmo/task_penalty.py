
if scan_for_left_post(360):
    if align_ball_and_left_post():
        rotate_left(48.5)
        move_forward(6.6)
        rotate_right(90)
        say("Going to shoot")
        kick()
        say("Goal!")
        show_happy()
else:
    if scan_for_right_post(360):
        if align_ball_and_right_post():
            rotate_right(48.5)
            move_forward(6.6)
            rotate_left(90)
            say("Going to shoot")
            kick()
            say("Goal!")
            show_happy()
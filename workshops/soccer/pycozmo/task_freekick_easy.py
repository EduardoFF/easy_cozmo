
if scan_for_left_post(360):
    dleft = distance_to_left_post()
    if scan_for_right_post(360):
        dright = distance_to_right_post()
        if dleft < dright: # Cozmo's on the left side
            if align_ball_and_right_post():
                rotate_right(48.5)
                move_forward(6.6)
                rotate_left(90)
                say("Going to shoot")
                if kick():
                    say("Goal!")
                    show_happy()
                else:
                    show_sad()
        else:
            if align_ball_and_left_post():
                rotate_left(48.5)
                move_forward(6.6)
                rotate_right(90)
                say("Going to shoot")
                if kick():
                    say("Goal!")
                    show_happy()
                else:
                    show_sad()

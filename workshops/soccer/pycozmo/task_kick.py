"""
Task: Kick

last time tested:2019-09-23
"""

if scan_for_ball(360):
    if align_with_ball():
        kick()
        show_happy()
    else:
        say("I can't find the ball")
        show_sad()
else:
    say("I can't find the ball")
    show_sad()
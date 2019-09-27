"""
Task: Find the captain


"""
i=2
while i < 3:
    move_forward(20)
    rotate_left(90)
    move_forward(15)
    rotate_left(90)
    move_forward(20)
    rotate_left(90)
    move_forward(15)
    rotate_left(90)
    if i==0:
        say("First lap")
    elif i==1:
        say("Second lap")
    elif i==2:
        say("Third lap")
    i=i+1

if scan_for_cube_by_id(360, 3):
    if align_with_cube_by_id(3):
        say("I found the captain")
        show_happy()
    else:
        show_sad()
else:
    show_sad()

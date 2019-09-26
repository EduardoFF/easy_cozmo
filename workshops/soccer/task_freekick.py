from easy_cozmo import *
from cozmo.util import degrees, Pose, distance_mm, speed_mmps

g = 300
delta = 50

def angle_to_rot(x1,x2, delta):
    print("x1=",x1," x2=",x2," delta",delta)
    beta = acosine((delta*delta -  x2*x2 + x1*x1)/(2*delta*x1))
    print("beta=",beta)
    a_lrb = asine(x1*sine(180-beta)/g)
    print("a_lrb=",a_lrb)
    dbr = g*sine(beta - a_lrb)/sine(180-beta)
    print("dbr=",dbr)
    alpha= atan(dbr - cosine(a_lrb)*g/2., sine(a_lrb)*g/2.)
    print("alpha=",alpha)
    return alpha


def cozmo_program():
    if align_ball_and_left_pole():
        if scan_for_right_pole(360):
            d1 = distance_to_right_pole()
            print("d1 = ", d1)
            if scan_for_ball(360):
                if align_with_ball():
                    move_backward(delta/10)
                    if scan_for_right_pole(360):
                        d2 = distance_to_right_pole()
                        print("d2 = ", d2)
                        if scan_for_ball(360):
                            if align_with_ball():
                                alpha = angle_to_rot(d1,d2,delta)
                                dd = cosine(90-alpha)*15
                                rotate(-1*(90-alpha))
                                move_forward(dd)
                                rotate(90)
                                kick()
                            else:
                                say("I cant align with the ball again")
                        else:
                            say("I cant find the ball again")








run_program_with_viewer(cozmo_program)

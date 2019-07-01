mindcraft._mycozmo.set_robot_volume(.1)
init_line_detection()
move_lift_ground()
while True:
    if not is_line_detected():
        stop()
    else:
        move_forward()
        angle = get_detected_line_angle()            
        if angle <= -30:
            steer_left(100)
        elif -30 < angle < -15:
            steer_left(50)
        elif -15 <= angle <= 15:
            steer_straight()
        elif 15 < angle <= 30:
            steer_right(50)
        elif 30 < angle:
            steer_right(100)

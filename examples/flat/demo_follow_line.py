#move_lift_ground()
while True:
    if not is_line_detected():
        stop()
    else:
        move()
        angle = get_detected_line_angle()            
        if angle <= -30:
            steer(-100)
        elif -30 < angle < -15:
            steer(-50)
        elif -15 <= angle <= 15:
            steer(0)
        elif 15 < angle <= 30:
            steer(50)
        elif 30 < angle:
            steer(100)

    

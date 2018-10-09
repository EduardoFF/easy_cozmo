from cozmo.util import radians
df_camera_auto_exposure_enabled = True  # best to use auto_exposure
df_image_stream_enabled = False
df_scan_cube_speed = 20 #in degrees
df_scan_face_speed = 17 #in degrees
df_pickup_retries=5
df_reverse_speed=50  # mmps
df_forward_speed=50  # mmps
df_use_headlight_for_scan_cube = True
df_forget_old_when_scanning_cubes=True
df_rotate_speed=30
df_move_relative_refined=True
df_align_refined=True
df_align_distance =150
df_volume=1
df_use_distance_threshold_for_cubes = True
df_distance_threshold_for_cubes = 500 # in mm
df_use_distance_threshold_for_objects = True
df_distance_threshold_for_objects = 400 # in mm
df_use_headlight_for_scan_object = True
df_forget_old_when_scanning_objects=True
df_scan_object_speed = 20 #in degrees

df_houghdetector_rho = 4
df_houghdetector_thetadiv = 50
df_houghdetector_threshold = 30
df_houghdetector_minlinelength = 50
df_houghdetector_maxlinegap = 255
df_houghdetector_lanedetection = True
df_houghdetector_singlelineoutput = True
df_houghdetector_horizon = 0.5
df_enable_line_detection = False # to enable it, call
                                 # line_detector.init_line_detection
df_line_detection_head_angle = -11

df_max_wheel_speed = 70 # in mmps


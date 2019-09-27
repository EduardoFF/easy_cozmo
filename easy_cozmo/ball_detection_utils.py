import cv2
try:
    from .cv_utils import region_of_interest
except Exception: #ImportError
    from easy_cozmo.cv_utils import region_of_interest

def color_segmentation(cvimage, **kwargs):
    blurred = cv2.GaussianBlur(cvimage, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    height, width, channels = cvimage.shape
    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    hsv_low = kwargs['hsv_low']
    hsv_high = kwargs['hsv_high']
    mask = cv2.inRange(hsv, hsv_low, hsv_high)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    mask_cropped = crop_image_for_ball(mask.copy(), width, height)
    mask = mask_cropped

    return mask

def crop_image_for_ball(cvimage, width, height):
    import numpy as np
    np.warnings.filterwarnings('ignore')

    region_of_interest_vertices = [
        (0, height),
        (0, 0.30*height),
        (width, 0.30*height),
        (width, height)
    ]
    cropped_image = region_of_interest(
        cvimage,
        np.array(
            [region_of_interest_vertices],
            np.int32
        ),
    )
    return cropped_image


def detect_ball(cvimage,tag=True, **kwargs):
    #%%
    # resize the frame, blur it, and convert it to the HSV
    # color space
    import imutils
    frame=cvimage

    height, width, channels = cvimage.shape

    mask = color_segmentation(frame,**kwargs)



    try:
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            # only proceed if the radius meets a minimum size
            if radius > 10:
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                if tag:
                    cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                return True, frame, (int(x),int(y)), radius
    except Exception as e:
        print(e)
    return False, frame, None, None

def get_ball_pnp(center, rad, **kwargs):
    import numpy as np
    np.warnings.filterwarnings('ignore')
    import cv2 as cv
    import math

    # some default values
    ballradius=21.35
    fx,fy = 277.345389059622, 278.253264643578
    cx,cy = 152.389201831827, 109.376457506074
    k1,k2=-0.0691655300978844,0.0630063731358772
    p1,p2=0,0

    camera_matrix = None
    if kwargs.__contains__('camera_matrix'):
        camera_matrix = kwargs['camera_matrix']
    else:
        camera_matrix=np.array([[fx,0,cx],
                             [0,fy,cy],
                             [0,0,1]])

    distortion_coef = None
    if kwargs.__contains__('distortion_coef'):
        distortion_coef = kwargs['distortion_coef']
    else:
        distortion_coef = np.array([k1,k2,p1,p2])

    if kwargs.__contains__('ball_radius'):
        ball_radius = kwargs['ball_radius']

    objp=np.array([[ballradius,0,0],
                   [0,-ballradius,0],
                   [0,ballradius,0],
                   [0,0,ballradius],
                   [0,0,-ballradius],
                   [ballradius*math.sin(math.pi/4.),ballradius*math.cos(math.pi/4.),0],
                   [ballradius*math.sin(math.pi/4.),-ballradius*math.cos(math.pi/4.),0],
                   [ballradius*math.sin(math.pi/4.),0,-ballradius*math.cos(math.pi/4.)],
                   [ballradius*math.sin(math.pi/4.),0,ballradius*math.cos(math.pi/4.)]

                   ])
    pts2=np.array([[center[0], center[1]],
                   [center[0]-rad,center[1]],
                   [center[0]+rad,center[1]],
                   [center[0],center[1]-rad],
                   [center[0],center[1]+rad],
                   [center[0]+rad*math.cos(math.pi/4.),center[1]],
                   [center[0]-rad*math.cos(math.pi/4.),center[1]],
                   [center[0],center[1]+rad*math.cos(math.pi/4.)],
                   [center[0],center[1]-rad*math.cos(math.pi/4.)],
                   ])
    ret,rvecs, tvecs = cv.solvePnP(objp, pts2, camera_matrix, distortion_coef)
    return ret, rvecs, tvecs

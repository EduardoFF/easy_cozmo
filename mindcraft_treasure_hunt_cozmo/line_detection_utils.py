import numpy as np
import cv2
import math
import sys

def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
 
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
 
	# return the edged image
	return edged
    
def mycanny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    return auto_canny(blurred)


def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    (assuming your grayscaled image is called 'gray')
    you should call plt.imshow(gray, cmap='gray')"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Or use BGR2GRAY if you read an image with cv2.imread()

def gaussian_blur(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def weighted_img(img, initial_img, α=0.8, β=1., λ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.
    `initial_img` should be the image before any processing.
    The result image is computed as follows:
    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, λ)

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def draw_lines(img, lines, color=[255, 255, 0], thickness=6):
    line_img = np.zeros(
        (
            img.shape[0],
            img.shape[1],
            3
        ),
        dtype=np.uint8
    )
    img = np.copy(img)
    if lines is None:
        return
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_img, (x1, y1), (x2, y2), color, thickness)
    img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)
    return img


# Auto-paramter Canny edge detection adapted from:
    # http://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
#def auto_canny(img, sigma=0.33):
#    blurred = cv2.GaussianBlur(img, (3, 3), 0)
#    v = np.median(blurred)
#    lower = int(max(0, (1.0 - sigma) * v))
#    upper = int(min(255, (1.0 + sigma) * v))
#    edged = cv2.Canny(blurred, lower, upper)
#    return edged

def average_lines(lines, h_y, centered=True, mid_x = 160, max_y = 240):
    xs = []
    ys = []
    for line in lines:
        if len(line) == 0:
            continue
        for l in line:
            if len(l) != 4:
                continue
            (x1, y1, x2, y2) = l
            if x1 != x2:
                slope = (y2 - y1) / (x2 - x1)
                if math.fabs(slope) < 0.5:
                    continue
            xs.extend([x1, x2])
            ys.extend([y1, y2])
    if len(ys) < 3:
        return None
    poly = np.poly1d(np.polyfit(
        ys,
        xs,
        deg=1
    ))
    if centered:
        h_y = int(max_y / 2)
        h_x = int(poly(h_y))
        b_y = max_y
        b_x = mid_x
        line = [h_x, h_y, mid_x, b_y]
        return line
    return None


""" expects an opencv image (BGR) """
def pipeline(image, **kwargs):
    """
    An image processing pipeline which will output
    an image with the lane lines annotated.
    """
    height, width, channels = image.shape
    
    gray_image = grayscale(image)
    img_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    mymask = gray_image
    BLUE = False
    YW=False
    if BLUE:
        lower_blue=np.array([100,150,0],np.uint8)
        upper_blue=np.array([140,255,255],np.uint8)
        mask_blue = cv2.inRange(img_hsv, lower_blue, upper_blue)
        mask_blue_image = cv2.bitwise_and(gray_image, mask_blue)
        mymask = mask_blue_image
    if YW:
        lower_yellow = np.array([20, 100, 100], dtype = "uint8")
        upper_yellow = np.array([30, 255, 255], dtype="uint8")
        mask_yellow = cv2.inRange(img_hsv, lower_yellow, upper_yellow)
        mask_white = cv2.inRange(gray_image, 200, 255)
        mask_yw = cv2.bitwise_or(mask_white, mask_yellow)
        mask_yw_image = cv2.bitwise_and(gray_image, mask_yw)
        mymask = mask_yw_image


    kernel_size = 5
    gauss_gray = gaussian_blur(mymask,kernel_size)
    
#    print("image has size {0} {1}".format(height,width))
    cannyed_image = auto_canny(gauss_gray, sigma=0.3)

#    region_of_interest_vertices = [
#        (0, height),
      #  (0, 0.75*height),
#        (width / 2, height / 2),
       # (width, 0.75*height),
#        (width, height)
#    ]

    region_of_interest_vertices = [
        (0.10*width, height),
        (0.10*width, 0.50*height),
        #(width / 2, height / 2),
        (0.90*width, 0.50*height),
        (0.90*width, height)
    ]
#    image_cvt = image.astype(np.uint8)
#    gray_image = cv2.cvtColor(image_cvt, cv2.COLOR_RGB2GRAY)
    #gray_image = cv2.cvtColor(image_cvt, cv2.COLOR_RGB2GRAY)
    #cannyed_image = cv2.Canny(gray_image, 100, 200)
#    cannyed_image = auto_canny(gray_image)
 
    cropped_image = region_of_interest(
        cannyed_image,
        np.array(
            [region_of_interest_vertices],
            np.int32
        ),
    )
#    return cv2.cvtColor(cannyed_image, cv2.COLOR_GRAY2BGR)
#    return cv2.cvtColor(mymask, cv2.COLOR_GRAY2BGR)
#    return cv2.cvtColor(gauss_gray, cv2.COLOR_GRAY2BGR)
#    return cv2.cvtColor(cropped_image, cv2.COLOR_GRAY2BGR)


#    return cropped_image
     #rho and theta are the distance and angular resolution of the grid in Hough space

    h_rho = kwargs.get("rho", 10)
    h_theta_div = kwargs.get("theta_div",60)
    h_threshold = kwargs.get("threshold", 30)
    h_minLineLength= kwargs.get("minLineLength",15)
    h_maxLineGap = kwargs.get("maxLineGap",5)
    lane_detection = kwargs.get("lane_detection", True)
     
    lines = cv2.HoughLinesP(
        cropped_image,
        rho=h_rho,
        theta=np.pi/h_theta_div,
        threshold=h_threshold,
        lines=np.array([]),
        minLineLength=h_minLineLength,
        maxLineGap=h_maxLineGap
    )
    #print(lines)
 
    left_line_x = []
    left_line_y = []
    right_line_x = []
    right_line_y = []


    if lines is not None and len(lines) > 0:
        line_image = image
        if lane_detection:
            for line in lines:
                for x1, y1, x2, y2 in line:

                    # if line is almost vertical, count it both as left and right
                    if abs(x2 - x1) < 2:
                        left_line_x.extend([x1, x2])
                        left_line_y.extend([y1, y2])
                        right_line_x.extend([x1, x2])
                        right_line_y.extend([y1, y2])
                        continue
                            
                    slope = (y2 - y1) / (x2 - x1)
                    if math.fabs(slope) < 0.5:
                        continue
                    if slope <= 0:
                        left_line_x.extend([x1, x2])
                        left_line_y.extend([y1, y2])
                    else:
                        right_line_x.extend([x1, x2])
                        right_line_y.extend([y1, y2])
            min_y = int(image.shape[0] * (2 / 5))
            max_y = int(image.shape[0])
            left_lane = []
            try:
                poly_left = np.poly1d(np.polyfit(
                    left_line_y,
                    left_line_x,
                    deg=1
                ))

                left_x_start = int(poly_left(max_y))
                left_x_end = int(poly_left(min_y))
                left_lane = [left_x_start, max_y, left_x_end, min_y]
            except:
                pass

            right_lane = []
            try:
                poly_right = np.poly1d(np.polyfit(
                    right_line_y,
                    right_line_x,
                   deg=1
                ))

                right_x_start = int(poly_right(max_y))
                right_x_end = int(poly_right(min_y))
                right_lane = [right_x_start, max_y, right_x_end, min_y]
            except:
                pass
#            print("Left lane ", left_lane)
#            print("Right lane ", right_lane)
            lines = []
            if len(left_lane):
                lines.append([left_lane])
            if len(right_lane):
                lines.append([right_lane])
        if kwargs['draw_lines']:
#            print("Drawing lines...")
            image = draw_lines(
                image,
                lines,
                color=[255,0,0],
                thickness=10
            )

        if kwargs['single_line_output']:
            if len(lines) >= 2:
                if (left_lane[3] - left_lane[1]) < 2:
                    lines = [[left_lane]]
                else:
                    ml = 1.0/((left_lane[2] - left_lane[0])/(left_lane[3] - left_lane[1]))
                    mr = 1.0/((right_lane[2] - right_lane[0])/(right_lane[3] - right_lane[1]))

                    xi = (ml*left_lane[0] - mr*right_lane[0] - left_lane[1]+right_lane[1])/(ml - mr)
                    yi = ml*(xi - left_lane[0]) + left_lane[1]
                    al = math.atan2(left_lane[3] - left_lane[1],
                                    left_lane[2] - left_lane[0])
                    ar = math.atan2(right_lane[3] - right_lane[1],
                                    right_lane[2] - right_lane[0])
                    mi = (math.sin(al)+math.sin(ar))/(math.cos(al) + math.cos(ar))
                    yi2 = max_y
                    xi2 = (max_y -yi + mi*xi)/mi
                    linei = [int(xi), int(yi), int(xi2), int(yi2)]
                    lines=[[linei]]

        if kwargs['draw_single_line']:
#            print("Drawing lines...")
            image = draw_lines(
                image,
                lines,
                color=[0,0,255],
                thickness=10
            )
        return lines, image
    return [[[]]], image

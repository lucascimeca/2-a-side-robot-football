import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

# Ouput binary image (will encode the thresholding)


cap = cv.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    frame = cv.blur(frame, (5,5))

    #hsv_frame
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # bin_out = np.ones((frame.shape[0], frame.shape[1]))

    # Color for red channel used to find thresholds
    # flat_red_nc = frame[:,:,0].ravel()
    # plt.hist(flat_red_nc, 1000)
    # plt.show()

    # Upon inspecting the histogram  (note this can be done algorithmically)
    # This is quite a complex image so the histogram method is not
    # the most effective
    # blurr = True
    # if blurr:
    #    norm_china2 =  cv.blur(frame,(5,5))
    # else:
    #    norm_china2 = frame

    # bin_out[norm_china2[:,:,0] < 155] = 0
    # bin_out[norm_china2[:,:,0] > 165 ] = 0
    # plt.gray()
    # plt.imshow(bin_out)
    # plt.show()

    # define the list of boundaries
    boundaries = [
        #([17, 15, 100], [50, 56, 200]),
        #([345,100,100], [360, 255, 255]),
        ([50, 50, 50], [30, 255, 255])
        #([160, 100, 100], [179, 255, 255])
        #([86, 31, 4], [220, 88, 50]),
        #([25, 146, 190], [62, 174, 250]),
        #([103, 86, 65], [145, 133, 128])
    ]

    # loop over the boundaries
    for (lower, upper) in boundaries:
        # create NumPy arrays from the boundaries
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
     
        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv.inRange(frame, lower, upper)
        output = cv.bitwise_and(frame, frame, mask = mask)
     
        # show the images
        cv.imshow("images", np.hstack([frame, output]))
        cv.waitKey(0)



    #if cv.waitKey(1) & 0xFF == ord('q'):
         #break





import cv2
import numpy as np
import glob

threshholds = [[],[],[],[],[],[]]
threshType = 0
image = cv2.imread("calibresult.png")

cap = cv2.VideoCapture(0)

def click_and_crop(event, x, y, flags, param):
	global refPt, cropping,threshholds,threshType,image

	if event == cv2.EVENT_LBUTTONDOWN:
		if(threshType == 0):
			threshholds[threshType].append((x,y))
		else:
			threshholds[threshType].append(image[y,x,:])
		print threshholds[threshType]




cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)

def listToThresh(ttype):
	data = np.array(threshholds[ttype])
	print data.shape
	print data
	dmin = np.amin(data,0)
	dmax = np.amax(data,0)
	return [dmax,dmin]

def preProcessCalib():
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((8*5,3), np.float32)
        objp[:,:2] = np.mgrid[0:8,0:5].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        images = glob.glob('../src/Preprocessing/Pitch0/*.png')

        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (8,5),None)
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)
                
                corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                imgpoints.append(corners2)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(img, (8,5), corners2,ret)
                
                #cv2.imshow('img',img)
                #cv2.waitKey(500)

        #cv2.destroyAllWindows()

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
        #img = cv2.imread('../Eyes/calib2/snap-unknown-20160208-155754-1.jpeg')
        h,  w = 480, 640
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

        # undistort
        mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
        return mapx,mapy

def preProcess(mapx,mapy,img):
	dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)
	#dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)
	kernel = np.ones((2,2), np.uint8)
	#opened = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel)
	#dilated = cv2.dilate(opened, kernel, iterations = 3)
	return dst

def order_points(pts):
	rect = np.zeros((4,2),dtype="float32")
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	return rect

def four_point_transform(image, pts):
	#obtain a consistent order of the points and unpack them individually
	rect = order_points(pts)
	(tl,tr,br,bl) = rect
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))

	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	dst = np.array([
		[0,0],
		[639,0],
		[639,479],
		[0,479]], dtype = "float32")

	M = cv2.getPerspectiveTransform(rect,dst)
	warped = cv2.warpPerspective(image,M,(640,480))
	return warped

def createImageSliders(name):
	cv2.createTrackbar('Hue Lower',name,0,180,nothing)
	cv2.createTrackbar('Hue Upper',name,10,180,nothing)
	cv2.createTrackbar('Sat Lower',name,191,255,nothing)
	cv2.createTrackbar('Val Lower',name,160,255,nothing)

def nothing(x):
	pass

mapx,mapy = preProcessCalib()
display = False
while True:
	_, image = cap.read()
	image = preProcess(mapx,mapy,image)
	
	if len(threshholds[0]) == 4:
		image = four_point_transform(image,np.asarray(threshholds[0]))
	
	cv2.imshow("image", image)
	key = cv2.waitKey(1) & 0xFF
	
	if key == ord("k"):
		break
	elif key == ord("r"):
		threshType = 1
		cv2.namedWindow('red')
		createImageSliders('red')

	if key == ord("s"):
		display = True
	if display:
		hu = cv2.getTrackbarPos('Hue Upper','red')
		hl = cv2.getTrackbarPos('Hue Lower','red')
		sl = cv2.getTrackbarPos('Sat Lower','red')
		vl = cv2.getTrackbarPos('Val Lower','red')
		lower = np.array([hl,sl,vl])
		upper = np.array([hu,255,255])
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		red_mask    = cv2.inRange(hsv, lower ,upper)
		# kernel_dilate = np.ones((2, 2), np.uint8)
		# close = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel_dilate)
		# close = cv2.morphologyEx(close,cv2.MORPH_CLOSE,kernel_dilate)
		kernel = np.ones((2,2), np.uint8)
		kernel2 = np.ones((5,5),np.uint8)
		frame_mask = cv2.dilate(red_mask, kernel)#, iterations=adjustments['erode'])
		close = cv2.morphologyEx(frame_mask, cv2.MORPH_CLOSE, kernel2)
		cv2.imshow("red",close)




print[(63, 51), (610, 69), (592, 447), (73, 449)]

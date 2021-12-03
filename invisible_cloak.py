import cv2
import numpy as np
from threading import Thread
import datetime
import threading
class WebcamVideoStream:
    def __init__(self, src="http://102.170.182.32:8080/video"):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True

def redd(frame):
        img=frame
        img_hsv=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red = np.array([77,50,0])
        upper_red = np.array([144,255,255])
        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)
        maskf = mask0
        output_img = img.copy()
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        maskf=cv2.morphologyEx(maskf, cv2.MORPH_OPEN, kernel2)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20,20))
        maskf=cv2.morphologyEx(maskf, cv2.MORPH_CLOSE, kernel)
        output_img[np.where(maskf==0)] = 0
        return output_img,maskf

camera = WebcamVideoStream().start()
bgModel=None
bgSubThreshold = 50
learningRate = 0
isBgCaptured = 0 
threshold=10
bg_frame=None
def printThreshold(thr):
    print("! Changed threshold to "+str(thr))

cv2.namedWindow('trackbar')
cv2.createTrackbar('trh1', 'trackbar', threshold, 100, printThreshold)
def removeBG(frame):
    fgmask = bgModel.apply(frame,learningRate=learningRate)
    kernel = np.ones((4, 4), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

while camera:
    frame = camera.read()
    cv2.imshow("original_frame",frame)
    frame = cv2.bilateralFilter(frame, 5, 50, 100)
    frame = cv2.flip(frame, 1)
    if isBgCaptured == 1:
        img=removeBG(frame)
        cv2.imshow('mask', img)
        maskk=img/255
        try :
            img2,maskk=redd(img)
        except:
            print("err")
        cv2.imshow('mask2', maskk)
        frame[np.where(maskk!=0)] = bg_frame[np.where(maskk!=0)]
        cv2.imshow('final', frame)
    k = cv2.waitKey(10)
    if k == 27: 
        break
    elif k == ord('b'):
        bg_frame=frame
        bgModel = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
        bgModel.setDetectShadows(False)
        isBgCaptured = 1
        print( '!!!Background Captured!!!')
    elif k == ord('r'):
        bgModel = None
        triggerSwitch = False
        isBgCaptured = 0
        print ('!!!Reset BackGround!!!')
    elif k == ord('n'):
        triggerSwitch = True
        print ('!!!Trigger On!!!')


            

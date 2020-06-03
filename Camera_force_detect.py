import cv2
import numpy as np
import imutils
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
from picamera import Color
from matplotlib import pyplot as plt

def nothing(x):
    pass

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
camera.iso = 80
camera.sensor_mode = 1
camera.awb_gains = 2

class boundedInt:

    def __init__(self, lower, upper):
        self.x = None
        if (lower <= upper):
            self.lower = lower
            self.upper = upper
        else:
            raise ValueError("Lower Bound must be lesser than Upper Bound".format())  

    def assign(self, x):
        if (x>= self.lower and x<=self.upper):
            self.x = x
            return self.x
        elif (x< self.lower):
            self.x = self.lower
            return self.x
        elif (x > self.upper):
            self.x = self.upper
            return self.x
        
class MatchColor:

    def __init__(self, in_min, in_max, out_min, out_max):
        self.x = 0
        self.inMin = in_min
        self.inMax = in_max
        self.outMin = out_min
        self.outMax = out_max        

    def mapColour(self, x):
        self.x = int((x - self.inMin) * (self.outMax - self.outMin) / (self.inMax - self.inMin) + self.outMin)
        return self.x 
       
myInt = boundedInt(20,152)
mpClr = MatchColor(20, 152, 210, 45)

rawCapture = PiRGBArray(camera, size=(640, 480))
start = time.time()

file = open("cam_free_displacement.txt", 'tw', encoding='utf-8')
file.write("start a new record ... \n")

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    # global thresholding
    ret1,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(img,(5,5),0)
    ret2,th2 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mean_val = cv2.mean(hsv, mask = th2)
    hue_cam = myInt.assign(round(mean_val[0]))
    hue_snr = mpClr.mapColour(hue_cam)
    cv2.putText(image, 'Hue:'+f"{hue_snr}", (200, 200), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0), 3)

    for c in contours:
        area = cv2.contourArea(c)
        if area >5000:
            cv2.drawContours(image, c, -1, (0,255,0), 3, cv2.LINE_AA)
            M = cv2.moments(c)
            cx = int(M["m10"]/M["m00"])
            cy = int(M["m01"]/M["m00"])
            cv2.circle(image,(cx,cy),7,(255,0,0), -1,)
            #cv2.putText(image, 'HSV:'+f"{hsv.mean():.3f}", (cx-20, cy-20), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0), 3)
            #mean_1 = cv2.mean(h, mask = th2)
            #cv2.putText(image, 'HSV:'+f"{mean_1:.3f}", (cx-20, cy-20), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0), 3)      
    cv2.imshow("frame", image)
    cv2.imshow("hsv", hsv)
    
    millis = int((time.time() - start)*1000)
    cv2.imshow("Global Thresholding", th1)
    cv2.imshow("Otsu binary", th2)
    print(millis, hue_snr, sep=',')
    file.write(str(millis) + ',' + str(hue_snr) + "\n")
    
    #plt.imshow(hsv)
    #plt.colorbar()
    #plt.show()
    key = cv2.waitKey(1)
    rawCapture.truncate(0)
    if key == 27:
        break
file.close()   
cv.destroyAllWindows()
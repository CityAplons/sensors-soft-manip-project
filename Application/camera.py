import cv2
import time
import io
import threading
from picamera.array import PiRGBArray
from picamera import PiCamera
from picamera import Color


class boundedInt:

    def __init__(self, lower, upper):
        self.x = None
        if (lower <= upper):
            self.lower = lower
            self.upper = upper
        else:
            raise ValueError("Lower Bound must be lesser than Upper Bound".format())

    def assign(self, x):
        if (x >= self.lower and x <= self.upper):
            self.x = x
            return self.x
        elif (x < self.lower):
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

class CameraHandler(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    stop_camera = False
    meanHSV = 0.0
    myInt = boundedInt(20, 152)
    mpClr = MatchColor(20, 152, 210, 45)

    def initialize(self):
        if CameraHandler.thread is None:
            # start background frame thread
            CameraHandler.thread = threading.Thread(target=self._thread)
            CameraHandler.thread.start()
            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        CameraHandler.last_access = time.time()
        self.initialize()
        buffer = PiRGBArray(self.frame, size=(640, 480))
        image = buffer.array
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # global thresholding
        ret1, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        ret2, th2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        mean_val = cv2.mean(hsv, mask=th2)
        hue_cam = self.myInt.assign(round(mean_val[0]))
        hue_snr = self.mpClr.mapColour(hue_cam)
        self.meanHSV = hue_snr
        cv2.putText(image, 'Hue:' + f"{hue_snr}", (200, 200), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 3)

        for c in contours:
            area = cv2.contourArea(c)
            if area > 5000:
                cv2.drawContours(image, c, -1, (0, 255, 0), 3, cv2.LINE_AA)
                M = cv2.moments(c)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(image, (cx, cy), 7, (255, 0, 0), -1, )
                # cv2.putText(image, 'HSV:'+f"{hsv.mean():.3f}", (cx-20, cy-20), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0), 3)
                # mean_1 = cv2.mean(h, mask = th2)
                # cv2.putText(image, 'HSV:'+f"{mean_1:.3f}", (cx-20, cy-20), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0), 3)

        # encode OpenCV raw frame to jpg and displaying it
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def getValues(self):
        return self.meanHSV

    def StopPreview(self):
        CameraHandler.stop_camera = True

    @classmethod
    def _thread(cls):
        with PiCamera() as camera:
            # camera setup
            camera.resolution = (640, 480)
            camera.framerate = 30
            camera.iso = 80
            camera.sensor_mode = 1
            camera.awb_gains = 2

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                cls.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
                elif CameraHandler.stop_camera is True:
                    break
        cls.thread = None

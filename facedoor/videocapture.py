import os
import settings
import time
from libprocess import LibThread

import cv2
from numpysocket import send_np, AsyncReceiver

class FaceDetectRequester(LibThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.to_process = None
        self.result = None
        self.result_receiver = AsyncReceiver(port=8882) #facedetect_service send face rectangle to this port 8882

    """
    register to detect face, asynchronously. so that method detect(im) exited as quick as possible
    result comes later in self.result
    """
    def detect(self, im):
        self.free.clear()
        self.to_process = im
        self.processing.set()

    def run(self):
        while True:
            if (self.processing.is_set()):
                gray = cv2.cvtColor(self.to_process, cv2.COLOR_BGR2GRAY)
                countstamp = self.result_receiver.countstamp
                send_np(gray,port=8881, verbose=True)
                time_start = time.time()
                while countstamp==self.result_receiver.countstamp:
                    if (time.time()-time_start>4):
                        print('no face detect result in 4 seconds')
                        break
                if (time.time()-time_start<=4):
                    # success
                    x,y,w,h = self.result_receiver.current_data.tolist()
                    face = gray[y:y + h, x:x + w]
                    cv2.imwrite('found.jpg',face)
                    print(x,y,w,h)
                time.sleep(5)
                self.processing.clear()
                self.free.set()
                
            else:
                time.sleep(0.1)
            

if __name__=='__main__':
    cam = cv2.VideoCapture(0)
    requester = FaceDetectRequester()
    requester.start()
    
    while True:
        s,im = cam.read()
        if requester.free.is_set():
            requester.detect(im)
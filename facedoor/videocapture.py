import os
import settings
import time
from libprocess import LibThread

import cv2
from communication_socket import send_np, AsyncReceiver

from facedetect_service import FaceDetectService
from facerecognize_service import FaceRecognizeService

TIMEOUT_DETECT = 3
TIMEOUT_RECOGNIZE = 5

class Requester(LibThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.to_process = None
        self.result = None
        self.facedetect_receiver = AsyncReceiver(port=settings.socket_port.face_detect.result) #facedetect_service send face rectangle to this port 8882
        self.facerecognize_receiver = AsyncReceiver(port=settings.socket_port.face_recognize.result) #face recognize result as in facerecognize_service

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
                # proceed detect image self.to_process
                gray = cv2.cvtColor(self.to_process, cv2.COLOR_BGR2GRAY)
                countstamp = self.facedetect_receiver.countstamp
                send_np(gray,port=settings.socket_port.face_detect.request, verbose=False)
                time_start = time.time()
                while countstamp==self.facedetect_receiver.countstamp:
                    if (time.time()-time_start>TIMEOUT_DETECT):
                        print('no face detect result in {} seconds'.format(TIMEOUT_DETECT))
                        break
                if countstamp!=self.facedetect_receiver.countstamp:
                    # success
                    x,y,w,h = self.facedetect_receiver.current_data.tolist()
                    if (w!=0 and h!=0):
                        face = gray[y:y + h, x:x + w]
                        # resize to ideal size
                        face = cv2.resize(face, settings.face_ideal_scale(face))
                        cv2.imwrite('found.jpg',face)
                        print(x,y,w,h)
                        # recognize this face
                        print(self.recognize(face))

                self.processing.clear()
                self.free.set()

            else:
                time.sleep(0.1)

    """
    @param face: grayscale, cropped, and sized face
    """
    def recognize(self,face):
        countstamp = self.facerecognize_receiver.countstamp
        print('requesting recognize')
        send_np(face,port=settings.socket_port.face_recognize.request)
        time_start = time.time()
        while countstamp==self.facerecognize_receiver.countstamp:
            if (time.time()-time_start>TIMEOUT_RECOGNIZE):
                print('no face recognize result in {} seconds'.format(TIMEOUT_RECOGNIZE))
                break
        if countstamp!=self.facerecognize_receiver.countstamp:
            result = ''.join([chr(d) for d in self.facerecognize_receiver.current_data.tolist()])
            return result

if __name__=='__main__':
    services = {#start services, they run as daemon
        'face detect': FaceDetectService(),
        'face recognize': FaceRecognizeService()
    }

    cam = cv2.VideoCapture(0)
    requester = Requester()
    requester.start()

    while True:
        s,im = cam.read()
        if requester.free.is_set():
            requester.detect(im)


import os
import settings
import time
from libprocess import LibThread

import numpy as np
import cv2
from communication_socket import send_np, AsyncReceiver

from facedetect_service import FaceDetectService
from facerecognize_service import FaceRecognizeService

TIMEOUT_DETECT = 3
TIMEOUT_RECOGNIZE = 5

def timestamp():
    return time.strftime("%Y%m%d%H%M%S")

class Requester(LibThread):
    def __init__(self, parent=None, person_name=''):
        super().__init__(parent)
        self.person_name=person_name
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
        lbph = cv2.face.LBPHFaceRecognizer_create()
        lbph_ready = False
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
                        # cv2.imwrite('found.jpg',face)
                        print(x,y,w,h)
                        # recognize this face
                        print('ready? ',lbph_ready)
                        try:
                            # raise Exception('python 3.4 doesnt work')
                            if not lbph_ready:
                                raise Exception('lbph not ready')
                            label,histogram_distance = lbph.predict(face)
                            if histogram_distance>40:
                                filename = settings.person_jpg_path_format.format(self.person_name)+'.jpg'
                                cv2.imwrite(filename)
                                print('distance () saved {}'.format(histogram_distance,filename))
                                images = np.asarray([face])
                                label = np.zeros(1)
                                lbph.update(images,label)
                            else:
                                print('distance {}. (not saving)'.format(histogram_distance))

                        except:
                            print('lbph not ready')
                            filename = os.path.join(settings.person_jpg_path_format.format(self.person_name),'a'+timestamp()+'.jpg')
                            cv2.imwrite(filename, face)

                            images = np.asarray([face])
                            label = np.asarray([1])
                            lbph.update(images,label)
                            lbph_ready = True

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
            histogram_distance = self.facerecognize_receiver.current_data[0]
            label = ''.join([chr(d) for d in self.facerecognize_receiver.current_data.tolist()])
            return histogram_distance,label

if __name__=='__main__':
    print('input person name')
    person = input()
    oldyaml = settings.person_lbph_path_format.format(person)+'.yaml'
    print('loading old yaml {}'.format(oldyaml))


    services = {#start services, they run as daemon
        'face detect': FaceDetectService(),
        # 'face recognize': FaceRecognizeService(maximum_hist_distance=9999999, specific_person_yaml='{}.yaml'.format(person))
    }

    cam = cv2.VideoCapture(0)
    requester = Requester(person_name=person)
    requester.start()

    while True:
        s,im = cam.read()
        if requester.free.is_set():
            requester.detect(im)

    print('keyboard interrupt')
    services['face detect'].stop()
    # services['face recognize'].stop()
    time.sleep(3)

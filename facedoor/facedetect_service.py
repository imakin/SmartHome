
import sys, os, shutil, time

import numpy as np
import cv2
import traceback
import settings

from communication_socket import receive_np, send_np

from libprocess import LibProcess

def main_program():
    print('makin2020\n running as service, waiting GRAY image to facedetect using communication_socket.py')
    print('reading input (ndarray image) from port 8881')
    print('result output ndarray[x,y,w,h] for the coordinate of the face in the input image, send to 127.0.0.1:8882')
    face_cascade_xml = os.path.join(settings.master_path, "xml/lbpcascades/lbpcascade_frontalface_improved.xml")
    face_cascade = cv2.CascadeClassifier(face_cascade_xml)
    while True:
        im = receive_np(port=settings.socket_port.face_detect.request, verbose=False)# already Converted it to grayscale for the faceCascade
        faces = face_cascade.detectMultiScale(# Find all the faces using the Cascade Classifier
            im,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        # draw a rectangle around the detected face
        if len(faces)==0:
            face_rect = (0,0,0,0)
        for (x, y, w, h) in faces:
            face_rect = x,y,w,h#loop and choose the latest
        print('disini {}'.format(face_rect))
#        face_detect.start_detect_if_free(im)
#        face_detect.run(once=True)
        result = np.ndarray(shape=(4,), dtype=np.uint32, buffer=np.array(face_rect))
        send_np(result, port=settings.socket_port.face_detect.result)


class FaceDetectService(LibProcess):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start()

    def run(self):
        main_program()

if __name__=='__main__':
    main_program()

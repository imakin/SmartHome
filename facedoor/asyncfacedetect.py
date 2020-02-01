
import sys, os, shutil

import numpy as np
import cv2
from multiprocessing import Process, Lock, Event
import traceback
import settings

class AsyncFaceDetect(Process):
    """
    serve:
        self.start_detect_if_free(image): image is the processed image, np.ndarray BGR
        self.processing
        self.free
        self.exited
    product:
        self.face_rectangle: a tupple containing (x,y,w,h) of detected face
        self.processing
        self.free

    """

    face_cascade_xml = os.path.join(settings.master_path, "lbpcascade_frontalface_improved_2.xml")
    faceright_cascade_xml = os.path.join(settings.master_path, "xml/haarcascades/haarcascade_profileface.xml")

    face_cascade = cv2.CascadeClassifier(face_cascade_xml)
    faceright_cascade = cv2.CascadeClassifier(faceright_cascade_xml)

    def __init__(self, parent=None):
        super(AsyncFaceDetect,self).__init__(parent)
        self.processing = Event()
        self.free = Event()
        self.processing.clear()
        self.free.clear()

        self.face_cascade_lock = Lock()

        self.daemon = True
        self.exited = Event()
        self.exited.clear()
        self.face_rectangle = (0,0,0,0)
        self.processed_image = None

    def start_detect_if_free(self, image):
        """
        @param image format BGR
        """
        if not self.free.is_set():
            self.processed_image = image
            self.free.set()
            return True
        return False

    def exit(self):
        self.exited.set()

    def run(self):

        while True:
            if self.exited.is_set():
                break
            self.free.wait()
            try:
                self.processing.set()
                gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)# Convert it to grayscale for the faceCascade
                self.face_cascade_lock.acquire()
                faces = self.face_cascade.detectMultiScale(# Find all the faces using the Cascade Classifier
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=4,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE,
                )
                self.face_cascade_lock.release()
                if len(faces)==0:
                    self.face_cascade_lock.acquire()
                    faces = self.faceright_cascade.detectMultiScale(# Find all the faces using the Cascade Classifier
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=4,
                        minSize=(30, 30),
                        flags=cv2.CASCADE_SCALE_IMAGE,
                    )
                    self.face_cascade_lock.release()
                    if len(faces)==0:
                        gray = np.fliplr(gray)
                        self.face_cascade_lock.acquire()
                        faces = self.faceright_cascade.detectMultiScale(# Find all the faces using the Cascade Classifier
                            gray,
                            scaleFactor=1.1,
                            minNeighbors=4,
                            minSize=(30, 30),
                            flags=cv2.CASCADE_SCALE_IMAGE,
                        )
                        self.face_cascade_lock.release()
                        if len(faces)!=0:
                            pass
                            img_w = gray.shape[1]
                            for i in range(len(faces)):
                                x,y,w,h = faces[i]
                                faces[i] = (img_w-x-w, y,w,h)
                        else:
                            self.face_rectangle = (0,0,0,0)


                # draw a rectangle around the detected face
                for (x, y, w, h) in faces:
                    self.face_rectangle = x,y,w,h
            except:
                traceback.print_exc()
            finally:
                self.free.clear()#process is done, only doing it again later if free is set again by HalFaceRecognizer
                self.processing.clear()

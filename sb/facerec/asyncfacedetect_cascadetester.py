
import sys, os, shutil
import time

import numpy as np
import cv2
import threading
import traceback
from PySide import QtCore

import const

def GetAsyncFaceDetectClass(thread_type=QtCore.QThread):
    """
    get the AsyncFaceDetect class
    instantiate example:
    fd = GetAsyncFaceDetectClass(threading.Thread)()
    """
    
    if thread_type!=QtCore.QThread and thread_type!=threading.Thread:
        raise ValueError("GetAsyncFaceDetectClass(thread_type=QtCore.QThread) thread_type must be QtCore.QThread or threading.Thread")
    
    class AsyncFaceDetect(thread_type):
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

        face_cascades = []

        def __init__(self, parent=None):
            super(AsyncFaceDetect,self).__init__(parent)
            self.processing = threading.Event()
            self.free = threading.Event()
            self.processing.clear()
            self.free.clear()
            
            self.face_cascade_lock = threading.Lock()
            
            self.daemon = True
            self.exited = threading.Event()
            self.exited.clear()
            self.face_rectangle = (0,0,0,0)
            self.processed_image = None
            
            for xml in os.listdir("xml/haarcascades"):
                self.face_cascades.append({
                    "xml":os.path.join("xml/haarcascades", xml),
                    "cascade":cv2.CascadeClassifier(os.path.join("xml/haarcascades", xml))
                })
            self.face_cascades_i = 0
            self.face_cascades_last_changed = time.clock()
            self.face_cascade = self.face_cascades[self.face_cascades_i]["cascade"]

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
                    
                    if (time.clock()-self.face_cascades_last_changed)>20:
                        self.face_cascades_i += 1
                        if self.face_cascades_i>=len(self.face_cascades):
                            self.face_cascades_i = 0
                        self.face_cascade = self.face_cascades[self.face_cascades_i]["cascade"]
                        self.face_cascades_last_changed = time.clock()
                    
                    print("face cascade {}".format(self.face_cascades[self.face_cascades_i]["xml"]))
                    
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
                        self.face_rectangle = (0,0,0,0)
                        
                    # draw a rectangle around the detected face
                    for (x, y, w, h) in faces:
                        self.face_rectangle = x,y,w,h
                except:
                    traceback.print_exc()
                finally:
                    self.free.clear()#process is done, only doing it again later if free is set again by HalFaceRecognizer
                    self.processing.clear()
    return AsyncFaceDetect

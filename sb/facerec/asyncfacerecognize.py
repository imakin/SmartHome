
import sys, os, shutil

import numpy as np
import cv2
import threading
import traceback
from PySide import QtCore
import time

import const

def GetAsyncFaceRecognizeClass(thread_type=QtCore.QThread):
    """
    get the AsyncFaceRecognize class
    instantiate example:
    fd = GetAsyncFaceRecognizeClass(threading.Thread)()
    """
    
    if thread_type!=QtCore.QThread and thread_type!=threading.Thread:
        raise ValueError("GetAsyncFaceRecognizeClass(thread_type=QtCore.QThread) thread_type must be QtCore.QThread or threading.Thread")
    
    class AsyncFaceRecognize(thread_type):
        """
        serve:
            self.start_recognize_if_free(image): image is the processed image, np.ndarray BGR
            self.processing
            self.free
            self.exited
            self.set_lbph
        product:
            self.face_rectangle: a tupple containing (x,y,w,h) of detected face
            self.processing
            self.free
        """

        face_cascade_xml = os.path.join(const.master_path, "lbpcascade_frontalface_improved_2.xml")
        face_cascade = cv2.CascadeClassifier(face_cascade_xml)

        def __init__(self, parent, recognized_queue):
            super(AsyncFaceRecognize,self).__init__(parent)
            self.processing = threading.Event()
            self.free = threading.Event()
            self.processing.clear()
            self.free.clear()
            
            self.recognized = recognized_queue
            
            self.face_cascade_lock = threading.Lock()
            
            self.daemon = True
            self.exited = threading.Event()
            self.exited.clear()
            self.face_rectangle = (0,0,0,0)
            self.processed_image = None
            
            self.lbphs = [None,] #list of LBPHFaceRecognizer from different levels (index is its level, starts from 1)
            self.lbphs = {}
            #~ if os.path.exists(const.train_db_all_filename_format.format(1)):
                #~ cv2.face.LBPHFaceRecognizer
                #~ lbph_l1 = cv2.face.LBPHFaceRecognizer_create()
                #~ x = lbph_l1.load(const.train_db_all_filename_format.format(1))
                #~ lbph_l1.train(const.train_db_all_filename_format.format(1))
                #~ self.lbphs.append(lbph_l1)
            self.last_predict_name = ""
            self.last_predict_time = time.clock()
                
        def set_lbph(self, lbph_object, level):
            self.lbphs[level] = lbph_object
            print(self.lbphs)
        
        

        def start_recognize_if_free(self, image):
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
                    print("async recognize started")
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
                        self.face_rectangle = (0,0,0,0)
                    
                    # draw a rectangle around the detected face
                    for (x, y, w, h) in faces:
                        self.face_rectangle = x,y,w,h
                        face = gray[y:y + h, x:x + w]
                        face = cv2.equalizeHist(face)
                        scale = const.face_ideal_height
                        face = cv2.resize(face, (int(w*scale/h),int(scale)))
                        level = 1
                        for level in self.lbphs:
                            lbph = self.lbphs[level]
                            if lbph==None:
                                continue
                            
                            print("predict started {}".format(level))
                            s = time.clock()
                            prediction = lbph.predict(face)
                            print("predict done {}".format(time.clock()-s))
                            label = lbph.getLabelInfo(prediction[0])
                            conf_float = prediction[1]
                            conf = int(conf_float)
                            print(label, conf)
                            
                            if conf>const.predict_max_confidence_distance:
                                print("i'm not confidence with this")
                                time.sleep(1)
                                continue
                            
                            if (
                                self.last_predict_name!=label
                                or
                                (time.clock()-self.last_predict_time>const.predict_minimum_repeated_interval)
                            ):
                                self.recognized.put((label, conf, level))
                                self.last_predict_time = time.clock()
                                self.last_predict_name = label
                                print("pushed")
                            else:
                                print("ignored")
                            time.sleep(1)
                        
                except:
                    traceback.print_exc()
                finally:
                    self.free.clear()#process is done, only doing it again later if free is set again by HalFaceRecognizer
                    self.processing.clear()
    return AsyncFaceRecognize

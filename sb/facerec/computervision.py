"""
Process image capturation from camera, and call computervision routines
"""
import sys, os, shutil

import numpy as np
import cv2
import threading
import traceback
from PySide import QtCore
from multiprocessing import Queue

from asyncfacedetect import GetAsyncFaceDetectClass
#~ from asyncfacedetect_cascadetester import GetAsyncFaceDetectClass

import asyncfacetrain
import asyncfacerecognize

import const

def GetComputerVisionClass(thread_type=QtCore.QThread):
    """
    get the ComputerVision class
    instantiate example:
    cv = GetComputerVisionClass(threading.Thread)()
    ComputerVision.async_facedetect threading class will follow thread_type
    """
    
    if thread_type!=QtCore.QThread and thread_type!=threading.Thread:
        raise ValueError("(thread_type=QtCore.QThread) thread_type must be QtCore.QThread or threading.Thread")
        
    class ComputerVision(thread_type):
        """
        
        serve:
            self.set_training_name
            self.set_mode
            self.set_recognize_target
        product:
            self.camera_image  take picture from camera and store it here
            self.recognized
            self.recognize_target
        """
        camera_image = None
        
        def __init__(self, parent=None):
            super(ComputerVision, self).__init__(parent)
            self.camera_image = None
            
            self.real_camera = cv2.VideoCapture(1)
            
            
            self.daemon = True
            self.exited = threading.Event()
            self.exited.clear()
            
            self.async_facedetect = GetAsyncFaceDetectClass(thread_type)(self)
            self.async_facedetect.start()
            
            self.async_facetrain = asyncfacetrain.GetAsyncFaceTrainClass(thread_type)(self)
            self.async_facetrain.start()
            
            self.recognized = Queue()
            
            self.async_facerecognize = asyncfacerecognize.GetAsyncFaceRecognizeClass(thread_type)(self, self.recognized)
            self.async_facerecognize.start()
            
            self.mode_recognize = object()
            self.mode_training = object()
            self.mode_training_name = "" #when capturing training, store it under this folder
            self.mode_training_captured = 0
            self.mode = self.mode_recognize
            
            self.lbph_l1 = None
            loaded = self.async_facetrain.start_load_if_free(50, self.set_lbph_l1)
            self.recognize_target = 50
            
        
        def set_mode(self, mode):
            if mode!=self.mode_recognize and mode!=self.mode_training:
                raise ValueError("mode!=self.mode_recognize and mode!=self.mode_training")
            self.mode = mode
            self.mode_training_captured = 0
        
        def set_training_name(self, name):
            self.mode_training_name = name
        
        def exit(self):
            self.async_facedetect.exit()
            self.exited.set()
            
        
        def set_lbph_l1(self, lbph_object):
            print("updating cb")
            self.lbph_l1 = lbph_object
            self.async_facerecognize.set_lbph(lbph_object, 1)
        
        
        def set_recognize_target(self, label):
            """
            change recognize target, 
            @param label can be integer or string
                when put integer, will load db_all with the value level. it means for each person found, take this number of its images if available
                when put string, will load db_{person} for the specific person only
            @return started or not. only started if thread is in idle
            """
            self.recognize_target = label
            return self.async_facetrain.start_load_if_free(label, self.set_lbph_l1)
        

        def run(self):
            try:
                while True:
                    if self.exited.is_set():
                        break
                    s, image = self.real_camera.read()
                    if not s:
                        continue
                    
                    if self.mode==self.mode_training and self.mode_training_captured<const.train_capture_per_call:
                        started = self.async_facetrain.start_capture_if_free(image, self.mode_training_name,0.2)
                        if started:
                            self.mode_training_captured += 1
                    elif self.mode_training_captured==const.train_capture_per_call:
                        started = self.async_facetrain.start_train_if_free(self.set_lbph_l1)
                        if started:
                            self.mode_training_captured = 1000
                            self.mode = self.mode_recognize
                    
                    
                    if self.mode==self.mode_recognize:
                        started = self.async_facerecognize.start_recognize_if_free(image)
                    
                    
                    #last one because it draws circles
                    self.async_facedetect.start_detect_if_free(image)
                        
                    
                    x,y,w,h = self.async_facedetect.face_rectangle
                    
                    self.camera_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    if (w>0 and h>0):
                        cv2.rectangle(self.camera_image, (x, y), (x + w, y + h), (255, 255, 255), 1)
            finally:
                self.real_camera.release()
    return ComputerVision


import sys, os, shutil

import numpy as np
import cv2
import threading
import traceback
from PySide import QtCore
import datetime
import time

import const

def GetAsyncFaceTrainClass(thread_type=QtCore.QThread):
    """
    get the AsyncFaceTrain class
    instantiate example:
    fd = GetAsyncFaceTrainClass(threading.Thread)()
    """
    
    if thread_type!=QtCore.QThread and thread_type!=threading.Thread:
        raise ValueError("GetAsyncFaceTrainClass(thread_type=QtCore.QThread) thread_type must be QtCore.QThread or threading.Thread")
    
    class AsyncFaceTrain(thread_type):
        """
        serve:
            self.start_capture_if_free( image is the processed image, np.ndarray BGR
            self.start_train_if_free
            self.processing
            self.free
            self.exited
        product:
            self.face_rectangle: a tupple containing (x,y,w,h) of detected face
            self.processing
            self.free
            
        """

        face_cascade_xml = os.path.join(const.master_path, "lbpcascade_frontalface_improved_2.xml")
        face_cascade = cv2.CascadeClassifier(face_cascade_xml)
        def __init__(self, parent=None):
            super(AsyncFaceTrain,self).__init__(parent)
            self.processing = threading.Event()
            self.free = threading.Event()
            self.processing.clear()
            self.free.clear()
            
            self.mode_capture = threading.Event()
            self.mode_train = threading.Event()
            self.mode_load = threading.Event()
            self.mode_capture.clear()
            self.mode_train.clear()
            self.mode_load.clear()
            
            self.face_cascade_lock = threading.Lock()
            
            self.daemon = True
            self.exited = threading.Event()
            self.exited.clear()
            self.face_rectangle = (0,0,0,0)
            self.processed_image = None
            self.person_name = ""
            self.person_folder = ""
            self.capture_delay_after = 0.5
            self.db_person = ""
            
            self.lbph_object = None
            self.callback_lbph_set = None
            self.lbph_load_label = 1    #when put integer, will load db_all with the value level. it means for each person found, take this number of its images if available
                                        #when put string, will load db_{person} for the specific person only
            
        
        def clear_mode(self):
            """
            when setting to idle, mode better be left cleared
            """
            for attr in dir(self):
                if attr.startswith("mode_"):
                    member = getattr(self, attr)
                    if type(member)==threading.Event:
                        member.clear()
        

        def start_capture_if_free(self, image, person_name, capture_delay_after=0.5):
            """
            @param image np.ndarray format BGR
            @param person_name the label will be used to create folder and store photos in it
            @param capture_delay_after: the delay after picture taken in second
            @return boolean : started or not
            """
            if not self.free.is_set():
                self.processed_image = image
                self.person_name = person_name
                self.capture_delay_after = capture_delay_after
                self.person_folder = const.train_folder_person_format.format(self.person_name)
                self.db_person = const.train_folder_person_format.format("{}.{}".format(self.person_name, const.train_db_filetype))
                
                if not os.path.exists(const.train_folder):
                    os.mkdir(const.train_folder)
                if not os.path.exists(self.person_folder):
                    os.mkdir(self.person_folder)
                
                self.clear_mode()
                self.mode_capture.set()
                self.free.set()
                
                return True
            return False
        
        
        def start_train_if_free(self, lbph_object_result_set):
            """
            create the train db
            @param lbph_object_result_set called when train is done with lbph_object as argument
                    lbph_object_result_set(lbph_object_lvl_1)
            """
            if not self.free.is_set():
                self.clear_mode()
                self.mode_train.set()
                self.callback_lbph_set = lbph_object_result_set
                self.free.set()
                return True
            return False
        
        
        def start_load_if_free(self, label, lbph_object_result_set):
            """
            create the train db
            @param label: 
                can be integer or string
                when put integer, will load db_all with the value level. it means for each person found, take this number of its images if available
                when put string, will load db_{person} for the specific person only
            @param lbph_object_result_set called when train is done with lbph_object as argument
                    lbph_object_result_set(lbph_object_lvl_1)
            """
            if not self.free.is_set():
                self.clear_mode()
                self.mode_load.set()
                self.lbph_load_label = label
                self.callback_lbph_set = lbph_object_result_set
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
                    if self.mode_capture.is_set():
                        self.process_capture()
                    
                    if self.mode_train.is_set():
                        self.process_train()
                    
                    if self.mode_load.is_set():
                        self.process_load()
                    
                except:
                    traceback.print_exc()
                finally:
                    self.free.clear()#process is done, only doing it again later if free is set again by HalFaceRecognizer
                    self.clear_mode()
                    self.processing.clear()
        
        
        
        
        def process_capture(self):
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
            
                print("capturing")
                
                face = gray[y:y + h, x:x + w]
                face = cv2.equalizeHist(face)
                scale = const.face_ideal_height
                face = cv2.resize(face, (int(w*scale/h),int(scale)))
                
                tm = datetime.datetime.now()
                name = str(tm.year)+str(tm.month).zfill(2)+str(tm.day).zfill(2)+str(tm.hour).zfill(2)+str(tm.minute).zfill(2)+str(tm.second).zfill(2)+str(tm.microsecond)+".jpg"
                cv2.imwrite(os.path.join(self.person_folder, name), face)
            time.sleep(self.capture_delay_after)
        
        
        
        
        
        def process_train(self):
            #for db all
            #take 1
            level = 1
            dbfilename = const.train_db_all_filename_format.format(level)
            images = []
            labels = []
            label_infos = []
            face_id = 0
            for person_name in os.listdir(const.train_folder):
                person_folder = os.path.join(const.train_folder, person_name)
                
                taken = 0
                if not os.path.isdir(person_folder):
                    continue
                for img in os.listdir(person_folder):
                    img_file = os.path.join(person_folder, img)
                    if taken<level:
                        #use this img_file
                        face_resize = cv2.imread(img_file, 0)
                        #confirmed local is already face_cascade-ed, take whole image
                        h = face_resize.shape[0]
                        w = face_resize.shape[1]
                        scale = const.face_ideal_height
                        face_resize = cv2.resize(face_resize, (int(w*scale/h),int(scale)))
                        images.append(np.asarray(face_resize, dtype=np.uint8))
                        labels.append(face_id)
                        label_infos.append(person_name)
                        print("processing", img_file)
                    else:
                        break
                    taken += 1
                face_id += 1
            
            if len(images)>0:
                (images, labels) = [np.asarray(lis) for lis in [images, labels]]
                if not (os.path.exists(const.train_folder)):
                    os.mkdir(const.train_folder)
                self.lbph_object = cv2.face.createLBPHFaceRecognizer()
                self.lbph_object.train(images, labels)
                for i in range(len(labels)):
                    self.lbph_object.setLabelInfo(labels[i], label_infos[i])
                self.lbph_object.save(dbfilename)
                
                try:
                    print("doing cb")
                    self.callback_lbph_set(self.lbph_object)
                except:
                    traceback.print_exc()
        
        
        
        def process_load(self):
            if type(self.lbph_load_label)==int:
                #Load all with level:
                level = self.lbph_load_label
                print("load for level {}".format(level))
                
                dbfilename = const.train_db_all_filename_format.format(level)
                images = []
                labels = []
                label_infos = []
                face_id = 0
                for person_name in os.listdir(const.train_folder):
                    person_folder = os.path.join(const.train_folder, person_name)
                    
                    taken = 0
                    if not os.path.isdir(person_folder):
                        continue
                    for img in os.listdir(person_folder):
                        img_file = os.path.join(person_folder, img)
                        if taken<level:
                            #use this img_file
                            face_resize = cv2.imread(img_file, 0)
                            #confirmed local is already face_cascade-ed, take whole image
                            h = face_resize.shape[0]
                            w = face_resize.shape[1]
                            scale = const.face_ideal_height
                            face_resize = cv2.resize(face_resize, (int(w*scale/h),int(scale)))
                            images.append(np.asarray(face_resize, dtype=np.uint8))
                            labels.append(face_id)
                            label_infos.append(person_name)
                            print("processing", img_file)
                        else:
                            break
                        taken += 1
                    face_id += 1
                
                if len(images)>0:
                    (images, labels) = [np.asarray(lis) for lis in [images, labels]]
                    if not (os.path.exists(const.train_folder)):
                        os.mkdir(const.train_folder)
                    self.lbph_object = cv2.face.createLBPHFaceRecognizer()
                    self.lbph_object.train(images, labels)
                    for i in range(len(labels)):
                        self.lbph_object.setLabelInfo(labels[i], label_infos[i])
                    self.lbph_object.save(dbfilename)
                    
                    try:
                        print("doing cb")
                        self.callback_lbph_set(self.lbph_object)
                    except:
                        traceback.print_exc()
            
            elif type(self.lbph_load_label)==str:
                person_name = self.lbph_load_label
                print("load specific for {}".format(person_name))
                
                dbfilename = const.train_db_all_filename_format.format(person_name)
                images = []
                labels = []
                label_infos = []
                face_id = 0
                
                person_folder = os.path.join(const.train_folder, person_name)
                
                taken = 0
                if not os.path.isdir(person_folder):
                    return
                for img in os.listdir(person_folder):
                    img_file = os.path.join(person_folder, img)
                    if taken<const.train_db_max_image_per_person:
                        #use this img_file
                        face_resize = cv2.imread(img_file, 0)
                        #confirmed local is already face_cascade-ed, take whole image
                        h = face_resize.shape[0]
                        w = face_resize.shape[1]
                        scale = const.face_ideal_height
                        face_resize = cv2.resize(face_resize, (int(w*scale/h),int(scale)))
                        images.append(np.asarray(face_resize, dtype=np.uint8))
                        labels.append(face_id)
                        label_infos.append(person_name)
                        print("processing", img_file)
                    else:
                        break
                    taken += 1
                
                if len(images)>0:
                    (images, labels) = [np.asarray(lis) for lis in [images, labels]]
                    if not (os.path.exists(const.train_folder)):
                        os.mkdir(const.train_folder)
                    self.lbph_object = cv2.face.createLBPHFaceRecognizer()
                    self.lbph_object.train(images, labels)
                    for i in range(len(labels)):
                        self.lbph_object.setLabelInfo(labels[i], label_infos[i])
                    self.lbph_object.save(dbfilename)
                    
                    try:
                        print("doing cb")
                        self.callback_lbph_set(self.lbph_object)
                    except:
                        traceback.print_exc()
        
    return AsyncFaceTrain

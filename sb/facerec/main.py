#!/usr/bin/env python
"""
main script. manage Qt
"""

import sys, os, shutil

import numpy as np
import cv2
import threading
import traceback
from PySide import QtCore, QtGui
import time

import computervision
import const

import ui

spacer_v = lambda: QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
spacer_h = lambda: QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)



class MainGUI(QtGui.QMainWindow):
    def __init__(self):
        """
        initiate a MainGUI app
        """
        super(MainGUI,self).__init__(None)
        
        self.computer_vision = computervision.GetComputerVisionClass()(self)
        self.computer_vision.start()
        
        self.cam_settings = {
            "res":{
                "w":const.cam_width, 
                "h":const.cam_height,
                "wh":(const.cam_width,const.cam_height)
            }
        }
        
        self.camera_stream_timer = QtCore.QTimer(self)
        self.camera_stream_timer.timeout.connect(self.camera_stream)
        self.camera_stream_timer.start(25)
        
        self.recognize_check_timer = QtCore.QTimer(self)
        self.recognize_check_timer.timeout.connect(self.recognize_check)
        self.recognize_check_timer.start(500)
        
        
        def ex():
            self.computer_vision.exit()
            exit(0)
        
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.gs_face_stream = QtGui.QGraphicsScene(self.ui.fr_face_stream)
        self.ui.gv_face_stream.setScene(self.ui.gs_face_stream)
        self.ui.gv_face_stream.setFixedSize(self.cam_settings["res"]["w"],self.cam_settings["res"]["h"])
        
        self.ui.bt_train.clicked.connect(self.start_train)
        
        self.show()
    
    
    def set_status(self, text):
        self.ui.lb_status.setText(text)
    
    
    def start_train(self):
        text, ok = QtGui.QInputDialog.getText(self, "Train person", "input person name") 
        if ok:
            self.computer_vision.set_training_name(text)
            self.computer_vision.set_mode(self.computer_vision.mode_training)
    
    
    def recognize_check(self):
        while not self.computer_vision.recognized.empty():
            #~ self.recognize_check_timer.stop()
            name, conf, level = self.computer_vision.recognized.get()
            #~ self.set_status("{}({}) lv({}) now for specific".format(name, conf,level))
            self.set_status("{}".format(name))
            #~ if type(self.computer_vision.recognize_target)==int:
                #~ self.set_status("{}({}) lv({}) now for specific".format(name, conf,level))
                #~ changed = self.computer_vision.set_recognize_target(name)
                #~ self.recognize_check_timer.start(2000)
            #~ elif type(self.computer_vision.recognize_target)==str:
                #~ self.set_status("{}({}) back to all".format(name, conf))
                #~ changed = self.computer_vision.set_recognize_target(5)
                #~ self.recognize_check_timer.start(2000)
    
    
    def camera_stream(self):
        """
        check face authenticate result if any
        """
        image = self.computer_vision.camera_image
        if image is not None:
            image = cv2.resize(image, self.cam_settings["res"]["wh"])
            qimg = QtGui.QImage(image, self.cam_settings["res"]["w"]-10, self.cam_settings["res"]["h"]-10, 
                           image.strides[0], QtGui.QImage.Format_RGB888)
            
            try:
                self.ui.gs_face_stream.removeItem(self.ui.gs_face_stream.items()[0])
            except:
                traceback.print_exc()
            self.cam_stream_pixmap = self.ui.gs_face_stream.addPixmap(QtGui.QPixmap.fromImage(qimg))
            
        else:
            pass
    
    def create_frame_grid(self, name, parent=None, force_widget_type=QtGui.QFrame):
        """
        create frame with name fr_{name} and grid with name igr_{name}
        if name starts with fr_, only one fr_ will be added in font of {name}
        grid will be set its margin and spacing to 0
        register fr_{name} and igr_{name} to self
        parent will be set to QFrame object parent
        @param force_widget_type default to QtGui.QFrame
        return frame,grid in tuple
        """
        if name.startswith("fr_"):
            name = name[3:]
        fr = force_widget_type(parent)
        fr.setObjectName("fr_"+name)
        igr = QtGui.QGridLayout(fr)
        igr.setContentsMargins(0,0,0,0)
        igr.setSpacing(0)
        igr.setObjectName("igr_"+name)
        fr.setLayout(igr)
        setattr(self, "fr_"+name, fr)
        setattr(self, "igr_"+name, igr)
        return fr,igr
    
        
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    a = MainGUI()
    sys.exit(app.exec_())


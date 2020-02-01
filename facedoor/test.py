import os, sys, shutil
import unittest
from PIL import Image
import cv2
import time

import settings

class FaceDetect(unittest.TestCase):
  
  def atest_detect(self):
    return
    from asyncfacedetect import AsyncFaceDetect
    
    self.cam = cv2.VideoCapture(0)
    cam = self.cam
    
#    im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
#    im_pil = Image.fromarray(im)
    
    self.facedetect = AsyncFaceDetect()
    facedetect = self.facedetect
    facedetect.start()
    
    while True:
      s,im = cam.read()
      self.assertTrue(s)
      gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
      cv2.imwrite('mem.jpg', gray)
      if not facedetect.start_detect_if_free('mem.jpg'):
        print("belum free")
        continue
      print(facedetect.face_rectangle)
      if (facedetect.face_rectangle!=(0,0,0,0)):
        cv2.imwrite('found.jpg',facedetect.processed_image)
        break
    
    cv2.imwrite('tes.jpg', im)
  
  def atest_cam(self):

#    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)

    if vc.isOpened(): # try to get the first frame
      rval, frame = vc.read()
    else:
      rval = False

    while rval:
      cv2.imshow("preview", frame)
      rval, frame = vc.read()
      key = cv2.waitKey(20)
      if key == 27: # exit on ESC
          break
    cv2.destroyWindow("preview")

  def atest_service(self):
    print("test asyncfacedetect as service")
    self.cam = cv2.VideoCapture(0)
    cam = self.cam
    file_input = 'asyncfacedetect.py_input.jpg'
    file_output = 'asyncfacedetect.py_output.jpg'
    train_file_format = 'train/makin/train_{}.jpg'
#    cv2.namedWindow("preview")
    train_count = 0
    while True:
      s,im = cam.read()
      self.assertTrue(s)
      gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
      cv2.imwrite(file_input, gray)
#      cv2.imwrite('copy.jpg', im)
      #continue
      while file_input in os.listdir():
        s,im = cam.read()
        time.sleep(0.1)
      if file_output in os.listdir():
        shutil.copy(file_output, train_file_format.format(train_count) )
        train_count += 1
        #imface = cv2.imread(file_output)
        print('train {}'.format(train_count))
        #print(len(imface))
        #break

  def test_train(self):
    lbph = cv2.face.LBPHFaceRecognizer_create()
    lbph.read('makin.yaml')
    file_output = 'asyncfacedetect.py_output.jpg'
    file_input = 'asyncfacedetect.py_input.jpg'
    
    self.cam = cv2.VideoCapture(0)
    cam = self.cam
    
    while True:
      s,im = cam.read()
      self.assertTrue(s)
      try:os.remove(file_output)
      except:pass
      cv2.imwrite(file_input, im)
      while (file_input in os.listdir()):
        s,im = cam.read()
        self.assertTrue(s)
      if not (file_output in os.listdir()):
        continue
      im = cv2.imread(file_output)
      im = cv2.resize(im, settings.face_ideal_scale(im))
      im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

      print(lbph.predict(im))


if __name__=="__main__":
  fd_test = unittest.main()

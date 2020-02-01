import unittest
from PIL import Image
import cv2
import time

class FaceDetect(unittest.TestCase):
  
  def test_detect(self):
    from asyncfacedetect import AsyncFaceDetect
    
    self.cam = cv2.VideoCapture(-1)
    cam = self.cam
    
#    im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
#    im_pil = Image.fromarray(im)
    
    self.facedetect = AsyncFaceDetect()
    facedetect = self.facedetect
    facedetect.start()
    
    while True:
      s,im = cam.read()
      self.assertTrue(s)
      self.assertTrue(facedetect.start_detect_if_free(im))
      while not facedetect.free.is_set():
        s,im = cam.read()
        cv2.imwrite('tes.jpg', im)
      print(facedetect.face_rectangle)
      if (facedetect.face_rectangle!=(0,0,0,0)):
        break
    
    cv2.imwrite('tes.jpg', im)
    
if __name__=="__main__":
  fd_test = unittest.main()
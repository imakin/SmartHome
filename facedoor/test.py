import unittest
from PIL import Image
import cv2
import time

class FaceDetect(unittest.TestCase):
  
  def atest_detect(self):
    # ~ return
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
  
  def test_cam(self):

    cv2.namedWindow("preview")
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

    
if __name__=="__main__":
  fd_test = unittest.main()

import os
import numpy as np
import cv2
import settings

if __name__=='__main__':
    print('input person name')
    person = input()
    oldyaml = settings.person_lbph_path_format.format(person)+'.yaml'
    person_jpg_folder = settings.person_jpg_path_format.format(person)
    print('for yaml {}'.format(oldyaml))
    print('using images in {}'.format())
    images = []
    for img_filename in os.listdir(person_jpg_folder):
        img_file = os.path.join(person_jpg_folder, img_filename)
        im = cv2.imread(img_file)
        images.append(np.asarray(im, dtype=np.uint8))
    images = np.asarray(images)
    labels = np.zeros(len(images))
    lbph_object = cv2.face.createLBPHFaceRecognizer()
    lbph_object.train(images, labels)
    lbph_object.save(oldyaml)
    print('saved to {}'.format(oldyaml))

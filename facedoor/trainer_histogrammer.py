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
    print('using images in {}'.format(person_jpg_folder))
    images = []
    for img_filename in os.listdir(person_jpg_folder):
        if not img_filename.endswith('jpg'):continue
        img_file = os.path.join(person_jpg_folder, img_filename)
        print(img_file)
        im = cv2.imread(img_file,cv2.IMREAD_GRAYSCALE)
        images.append(np.asarray(im, dtype=np.uint8))
    images = np.asarray(images)
    labels = np.asarray([0]*len(images))
    print(labels)
    lbph_object = cv2.face.LBPHFaceRecognizer_create()
    lbph_object.train(images, labels)
    lbph_object.save(oldyaml)
    print('saved to {}'.format(oldyaml))

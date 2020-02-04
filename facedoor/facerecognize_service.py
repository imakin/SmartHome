"""
makin 202
"""

import sys, os, shutil

import numpy as np
import cv2

import settings
from communication_socket import receive_np, send_np

from libprocess import LibProcess

def main_program():
    print('makin2020\n running as service, waiting GRAY face image to recognize using communication_socket.py')
    print('reading input (ndarray image) from port 8883')
    print('result output ndarray[x,y,w,h] for the coordinate of the face in the input image, send to 127.0.0.1:8884')

    lbph_pool = []
    for yaml in os.listdir(settings.person_lbph_path):
        lbph = cv2.face.LBPHFaceRecognizer_create()
        print('loaded {}'.format(settings.person_lbph_path_format.format(yaml)))
        lbph.read(settings.person_lbph_path_format.format(yaml))
        lbph_pool.append({
            'label':yaml.replace('.yaml',''),
            'lbph':lbph
        })

    while True:
        face = receive_np(port=settings.socket_port.face_recognize.request)
        lowest_histogram_distance = 300
        lowest_histogram_label = ''
        for lbph_dict in lbph_pool:
            lbph = lbph_dict['lbph']
            label = lbph_dict['label']
            label_id,histogram_distance = lbph.predict(face)
            print(histogram_distance)
            if (histogram_distance<lowest_histogram_distance):
                lowest_histogram_distance = histogram_distance
                lowest_histogram_label = label
        if (lowest_histogram_distance<50):
            result_str = '{} ({})'.format(lowest_histogram_label, int(lowest_histogram_distance))
            print(result_str)
            result = np.ndarray(shape=(len(lowest_histogram_label),), dtype=np.uint32, buffer=np.array([ord(c) for c in result_str]))
            send_np(result, port=settings.socket_port.face_recognize.result)


class FaceRecognizeService(LibProcess):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start()

    def run(self):
        main_program()



if __name__=='__main__':
    main_program()

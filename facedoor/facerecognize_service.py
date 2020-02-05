"""
makin 202
"""

import sys, os, shutil

import numpy as np
import cv2

import settings
from communication_socket import receive_np, send_np

from libprocess import LibProcess

stopped = False
def main_program(maximum_hist_distance=50, specific_person_yaml=None):
    print('makin2020\n running as service, waiting GRAY face image to recognize using communication_socket.py')
    print('reading input (ndarray image) from port 8883')
    print('result output ndarray[histogram_distance, label_char[0], label_char[1], label_char[2]...] for the coordinate of the face in the input image, send to 127.0.0.1:8884')

    lbph_pool = []
    if specific_person_yaml==None:
        for yaml in os.listdir(settings.person_lbph_path):
            if not yaml.endswith('yaml'):continue
            lbph = cv2.face.LBPHFaceRecognizer_create()
            print('loaded {}'.format(settings.person_lbph_path_format.format(yaml)))
            lbph.read(settings.person_lbph_path_format.format(yaml))
            lbph_pool.append({
                'label':yaml.replace('.yaml',''),
                'lbph':lbph
            })
    else:
        lbph = cv2.face.LBPHFaceRecognizer_create()
        print('loaded {}'.format(settings.person_lbph_path_format.format(specific_person_yaml)))
        lbph.read(settings.person_lbph_path_format.format(specific_person_yaml))
        lbph_pool.append({
            'label':specific_person_yaml.replace('.yaml',''),
            'lbph':lbph
        })

    while not stopped:
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
        if (lowest_histogram_distance<maximum_hist_distance):
            result_buffer = [int(lowest_histogram_distance)]
            result_buffer = result_buffer + [ord(c) for c in result_str]
            result = np.ndarray(shape=(len(result_buffer)+1,), dtype=np.int, buffer=np.array(result_buffer))
            send_np(result, port=settings.socket_port.face_recognize.result)


class FaceRecognizeService(LibProcess):
    def __init__(self, parent=None, maximum_hist_distance=50, specific_person_yaml=None):
        super().__init__(parent)
        self.maximum_hist_distance = maximum_hist_distance
        self.specific_person_yaml = specific_person_yaml
        self.start()

    def stop(self):
        global stopped
        stopped = True
        
    def run(self):
        main_program(maximum_hist_distance=self.maximum_hist_distance, specific_person_yaml=self.specific_person_yaml)



if __name__=='__main__':
    main_program()

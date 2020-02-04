import sys, os, shutil

executed_file = sys.argv[0]
if executed_file!="":
  master_path = os.path.dirname(os.path.realpath(executed_file))
else:
  master_path = os.path.realpath(executed_file)
print("master path: {}".format(master_path))

person_path = os.path.join(master_path, 'person')
person_jpg_path = os.path.join(person_path, 'jpg')
person_jpg_path_format = os.path.join(person_jpg_path, '{}')
person_lbph_path = os.path.join(person_path, 'lbph')
person_lbph_path_format = os.path.join(person_lbph_path, '{}')

face_ideal_resolution = (180,180)
face_ideal_width = face_ideal_resolution[0]
face_ideal_height = face_ideal_resolution[1]

def face_ideal_scale(face):
  h = face.shape[0]
  w = face.shape[1]
  scale = face_ideal_height
  return ( int(w*scale/h), int(scale) )

socket_port = {
    'face_detect': {
        'request': 8881,
        'result' : 8882,
    },
    'face_recognize': {
        'request': 8883,
        'result' : 8884,
    }
}
class socket_port:
    class face_detect:
        request = 8881
        result = 8882
    class face_recognize:
        request = 8883
        result = 8884

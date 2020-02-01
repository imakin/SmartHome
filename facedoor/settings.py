import sys, os, shutil

executed_file = sys.argv[0]
if executed_file!="":
  master_path = os.path.dirname(os.path.realpath(executed_file))
else:
  master_path = os.path.realpath(executed_file)
print("master path: {}".format(master_path))

face_ideal_resolution = (180,180)
face_ideal_width = face_ideal_resolution[0]
face_ideal_height = face_ideal_resolution[1]

def face_ideal_scale(face):
  h = face.shape[0]
  w = face.shape[1]
  scale = face_ideal_height
  return ( int(w*scale/h), int(scale) )

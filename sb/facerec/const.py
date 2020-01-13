import sys, os, shutil

executed_file = sys.argv[0]
if executed_file!="":
	master_path = os.path.dirname(os.path.realpath(executed_file))
else:
	master_path = os.path.realpath(executed_file)
print("master path: {}".format(master_path))


cam_width = 800
cam_height = 600

face_ideal_resolution = (180,180)
face_ideal_width = face_ideal_resolution[0]
face_ideal_height = face_ideal_resolution[1]

train_folder = os.path.join(master_path, "train")
train_folder_person_format = os.path.join(master_path, "train", "{}") #usage train_folder_person_format.format(person_name)

train_capture_per_call = 10
train_db_filetype = "yaml"
train_db_all_filename = os.path.join(train_folder, "all.{}".format(train_db_filetype))
train_db_all_filename_format = os.path.join(train_folder, "all_{{}}.{}".format(train_db_filetype)) #usage train_db_all_lv_filename_format.format(level)

train_db_max_image_per_person = 100

predict_minimum_repeated_interval = 2 #in seconds, when same result returned, only update result if last result is more than this value

predict_max_confidence_distance = 42

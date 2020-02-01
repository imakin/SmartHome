import sys, os, shutil

executed_file = sys.argv[0]
if executed_file!="":
	master_path = os.path.dirname(os.path.realpath(executed_file))
else:
	master_path = os.path.realpath(executed_file)
print("master path: {}".format(master_path))

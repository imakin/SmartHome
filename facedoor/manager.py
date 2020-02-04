import subprocess

subprocess.run('python facedetect_service.py &',shell=True)
subprocess.run('python facerecognize_service.py &',shell=True)

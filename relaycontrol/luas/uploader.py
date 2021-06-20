#!/usr/bin/env python
#encoding utf8
import requests
import re
from sys import argv
import pathlib
import shutil
print(f"{argv[0]} [filename] [ipaddress to upload]")

filename = argv[1]
address = argv[2]
tmpdir = "/tmp/makin-httpupload"
pathlib.Path(tmpdir).mkdir(parents=True, exist_ok=True)
with open(filename) as f:
    script = ""
    end_command_mark = "]]"
    commented_out = False
    banyaksamadengan = 0
    for line in f:
        originalline = line
        line = line.strip()
        if line.startswith("--"):
            if line.startswith("--["):
                # ignore multiline comment
                if line.startswith("--[="):
                    #todo:
                    #note: only support comment 
                    banyaksamadengan = len(re.findall("\[(=+)\]",line)[0])
                    samadengan = "="*banyaksamadengan
                    end_command_mark = f"]{samadengan}]"
                else:
                    banyaksamadengan = 0
                    end_command_mark = "]]"
                commented_out = True
            else:
                #ignore comment
                #its a line comment --
                continue
        if commented_out:
            pos = line.find(end_command_mark)
            if pos>0:
                #end of commented out! 
                #todo: 
                #note: doesnt support mix of commented words and uncommented words in the same line
                continue
                # ~ if (pos==0):
                    # ~ non_commented_line = line.replace(end_command_mark, "")
                # ~ else:
                    # ~ samadengan = "="*banyaksamadengan
                    # ~ non_commented_line = re.findall(".*\]"+samadengan+"\](.*)",line)[0]
                    # ~ #TODO: 
                    # ~ #note: doesn't support another comment after comment off in the same line
                    # ~ script += non_commented_line
            else:
                #still inside comment
                continue
        else:
            script += originalline
print(f"saving minimized file as {tmpdir+'/'+filename}")
with open(tmpdir+'/'+filename, "w") as f:
    f.write(script)
print("uploading with protocol: http, file:that minimzed file, method: post")
with open(tmpdir+'/'+filename, 'rb') as f:
    requests.post(f"http://{address}",files={"file":f})

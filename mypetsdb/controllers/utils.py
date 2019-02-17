import os
import json
import sys

def loadConfig():
   contents = open('/etc/config/mypetsdb.json', 'r').read()
   config = json.loads(contents)

   dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../../'
   config['TOP_LEVEL_DIR'] = dir_path

   return(config)


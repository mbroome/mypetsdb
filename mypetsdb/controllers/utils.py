import os
import json

def loadConfig():
   contents = open('/etc/config/mypetsdb.json', 'r').read()
   config = json.loads(contents)

   return(config)


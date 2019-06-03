import os
import sys
import json

dirPath = os.path.dirname(os.path.realpath(__file__))

class ConfigLoader():
   def __init__(self, configFiles=[]):
      self.configFileList = configFiles
      self.config = {}

      # see if we can find the file in the dir tree
      if not self.configFile:
         p = dirPath
         while p:
            c = p + '/settings.json'
            if os.path.exists(c):
               self.configFileList.insert(0, c)
            p = p[:p.rfind('/')]
         
      # is there one in /etc/config
      self.configFileList.append('/etc/config/settings.json')

      # what about one set in the environment
      if 'APP_CONFIG' in os.environ:
         self.configFileList.append(os.environ['APP_CONFIG'])

      for f in self.configFileList:
         self.mergeConfig(f)

      #self.config['TOP_LEVEL_DIR'] = os.path.dirname(os.path.realpath(__file__)) + '/../'
      self.config['TOP_LEVEL_DIR'] = os.path.dirname(os.path.realpath(__file__))

      # pick the section of the config based on the APP_ENV
      if 'APP_ENV' in os.environ:
         for f in self.configFileList:
            self.mergeConfig(f, os.environ['APP_ENV'])

      # override configs with environment variables, if set
      for key in os.environ.keys():
         if key.startswith('APP_'):
            k = key[4:]
            self.config[k] = os.environ[key]

   def __getattr__(self, key):
      if key in self.config:
         return(self.config[key])
      else:
         return(False)

   def mergeConfig(self, configFile, section='default'):
      # parse up the config file
      try:
         content = open(configFile, 'r').read()
         data = json.loads(content)
      except Exception, e:
         #print e
         pass

      try:
         self.config.update(data[section])
      except Exception, e:
         #print e
         pass

settings = ConfigLoader()


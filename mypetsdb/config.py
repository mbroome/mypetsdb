import os
import sys
import json

dirPath = os.path.dirname(os.path.realpath(__file__))

class ConfigLoader():
   def __init__(self, configFile=''):
      self.configFile = configFile
      self.config = {}

      # see if we can find the file in the dir tree
      if not self.configFile:
         p = dirPath
         while p:
            c = p + '/settings.json'
            if os.path.exists(c):
               self.configFile = c
               break
            p = p[:p.rfind('/')]
         
      # is there one in /etc/config
      if not self.configFile:
         if os.path.exists('/etc/config/settings.json'):
            self.configFile = '/etc/config/settings.json'

      # what about one set in the environment
      if 'APP_CONFIG' in os.environ:
         self.configFile = os.environ['APP_CONFIG']

      # parse up the config file
      content = open(self.configFile, 'r').read()
      data = json.loads(content)

      # of there is a 'default' section, populate it
      if 'default' in data:
         self.config = data['default'].copy()


      self.config['TOP_LEVEL_DIR'] = os.path.dirname(os.path.realpath(__file__)) + '/../'

      # pick the section of the config based on the APP_ENV
      if 'APP_ENV' in os.environ:
         if os.environ['APP_ENV'] in data:
            self.config.update(data[ os.environ['APP_ENV']])

      # override configs with environment variables, if set
      for key in os.environ.keys():
         if key.startswith('APP_'):
            k = key[4:]
            self.config[k] = os.environ[key]

   def __getattr__(self, key):
      return self.config[key]

settings = ConfigLoader()


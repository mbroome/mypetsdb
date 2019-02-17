#!/usr/bin/env python
import sys
import json
import string
import time
import csv
import glob

import pprint
pp = pprint.PrettyPrinter(indent=4)

csv.field_size_limit(sys.maxsize)

classificationFile = '/home/mbroome/src/mypetsdb/data/classifications.json'

csvDir = '/home/mbroome/tmp/iucn/'
keyList = [
           'assessmentDate',
           'redlistCategory',
           'internalTaxonId',
           'possiblyExtinct',
          ]

content = open(classificationFile, 'r').read()
classifications = json.loads(content)
def classLookup(s):
   for row in classifications:
      if row['classification'].lower() == s.lower():
         if len(row['key']) != 3:
            return(row['key'].lower())


data = {}
for f in glob.glob(csvDir + '*.csv'):

   reader = csv.DictReader(open(f, 'r'))
   for row in reader:
      #pp.pprint(row)
      if data.has_key(row['internalTaxonId']):
         data[row['internalTaxonId']].update(row)
      else:
         data[row['internalTaxonId']] = row.copy()

#print(len(data))
#print(data['10267'])
#print(json.dumps(data['10267']))
processed = []
for row in data:
   rec = {}
   for k in keyList:
      if k.lower() == 'redlistcategory':
         rec[k.lower()] = classLookup(data[row][k].lower())
      else:
         rec[k.lower()] = data[row][k].lower()

   rec['scientific_name'] = data[row]['genusName'].lower() + ' ' + data[row]['speciesName'].lower()
   processed.append(rec)

print(json.dumps(processed))


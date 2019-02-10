#!/usr/bin/env python
from __future__ import print_function
import sys
from functools import partial

import json
import string
import time
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

import pprint
pp = pprint.PrettyPrinter(indent=4)

error = partial(print, file=sys.stderr)

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


speciesPages = {}

hostname = 'https://en.wikipedia.org/wiki/List_of_dog_breeds'

def getTopLevelPage():
   raw_html = simple_get(hostname)
   html = BeautifulSoup(raw_html.decode('utf-8','ignore'), 'html.parser')
   table = html.find(class_="wikitable sortable")

   #pp.pprint(table)

   data = []
   for row in table.find_all('tr'):
      #print(row)
      variety = ''
      cols = row.find_all('td')
      try:
         #print(cols[0])
         variety = cols[0].find('a').text
      except:
         try:
            variety = cols[0].find('b').text
         except:
            pass
      if variety:
         rec = {'variety': variety.lower(),
                'scientific_name': 'canis lupus familiaris',
                'source': 'dog-wikipedia'}
         data.append(rec)

   return(data)

data = getTopLevelPage()
print(json.dumps(data))



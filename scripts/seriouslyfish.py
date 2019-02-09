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

hostname = 'https://www.seriouslyfish.com'

def getTopLevelPage():
   url = hostname + '/knowledge-base/'
   raw_html = simple_get(url)
   html = BeautifulSoup(raw_html.decode('utf-8','ignore'), 'html.parser')
   profiles = html.findAll(class_='profilesbox')

   #print(profiles)

   pages = {}
   for profile in profiles:
      for i, p in enumerate(profile.select('a')):
         pages[p.get('href')] = True

   return(pages)

def getGroupPage(url):
   #print "Getting url: " + url
   time.sleep(2)
   error(url)
   raw_html = simple_get(url)
   if not raw_html:
      error('no content for: ' + url)
   html = BeautifulSoup(raw_html.decode('utf-8','ignore'), 'html.parser')
   profiles = html.findAll(class_='profile_title')

   #pp.pprint(profiles)
      
   for profile in profiles:
      for i, p in enumerate(profile.select('a')):
         speciesPages[p.get('href')] = True

   nextPage = html.find(class_='next')
   if nextPage:
      nextUrl = nextPage.get('href')
      getGroupPage(nextUrl)


groupPages = getTopLevelPage()
for gp in groupPages:
   getGroupPage(gp)

data = []
for link in speciesPages:
   #print link
   species = link[link.find('/species/') + 9:]
   species = species.replace('/', '').replace('-', ' ')
   #print species
   rec = {'scientific_name': species,
          'link': link}
   data.append(rec)

print(json.dumps(data))


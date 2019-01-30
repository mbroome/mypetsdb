#!/usr/bin/env python
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

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


data = {"species":[],
        "classifications":[]}

hostname = 'https://caresforfish.org/'

def getTopLevelPage():
   pid = 40
   raw_html = simple_get(hostname +'?page_id=%s' % pid)
   html = BeautifulSoup(raw_html.decode('utf-8','ignore'), 'html.parser')
   tags = html.find(class_='entry-content')

   pages = []
   for i, p in enumerate(tags.select('a')):
      pages.append(p.get('href'))

   return(pages)


def getSpeciesPage(page):
   #pid = 297
   #pid = 317
   #pid = 257
   #pid = 401
   link = hostname + page
   raw_html = simple_get(link)
   html = BeautifulSoup(raw_html.decode('utf-8','ignore'), 'html.parser')
   body = html.find(class_='entry-content')
   tbody = body.find('tbody')
   #print(tbody)

   species = []
   for i, row in enumerate(tbody.find_all('tr')):
      #print(':::')
      #print(row)
      #print(':::')

      cols = row.find_all('td')
      cols = [ele.text.strip() for ele in cols]
      #data.append([ele for ele in cols if ele])
      rec = {}
      rec['species'] = cols[0].replace(u"\u2018", "'").replace(u"\u2019", "'").encode('ascii',errors='ignore')
      rec['classification'] = cols[1]
      rec['assessment'] = cols[2]
      rec['authority'] = cols[3]
      rec['link'] = link
      species.append(rec)

   return(species)

def getClassifications():
   pid = 464
   raw_html = simple_get(hostname +'?page_id=%s' % pid)
   html = BeautifulSoup(raw_html.decode('utf-8','ignore'), 'html.parser')
   body = html.find(class_='entry-content')

   tables = body.find_all(class_="directory")
   #tables = body.find_all('table')

   cls = []
   for table in tables:
      #print(':::')
      tbody = table.find('tbody')
      #print(tbody)
      #print(':::')
   
      for i, row in enumerate(tbody.find_all('tr')):
         cols = row.find_all('td')
         cols = [ele.text.strip() for ele in cols]
         #data.append([ele for ele in cols if ele])
         rec = {}
         rec['key'] = cols[0]
         rec['classification'] = cols[1]
         rec['description'] = cols[2].replace(u"\u2018", "'").replace(u"\u2019", "'").encode('ascii',errors='ignore')
         cls.append(rec)

   return(cls)

pages = getTopLevelPage()
for page in pages:
   d = getSpeciesPage(page)
   data['species'] += d

data['classifications'] = getClassifications()

print(json.dumps(data, ensure_ascii=False))


#!/usr/bin/env python
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


data = []
hostname = 'https://caresforfish.org/'

def getTopLevelPage():
   pid = 40
   raw_html = simple_get(hostname +'?page_id=%s' % pid)
   html = BeautifulSoup(raw_html, 'html.parser')
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
   raw_html = simple_get(hostname + page)
   html = BeautifulSoup(raw_html, 'html.parser')
   body = html.find(class_='entry-content')
   tbody = body.find('tbody')
   #print(tbody)

   data = []
   for i, row in enumerate(tbody.find_all('tr')):
      #print(':::')
      #print(row)
      #print(':::')

      cols = row.find_all('td')
      cols = [ele.text.strip() for ele in cols]
      #data.append([ele for ele in cols if ele])
      rec = {}
      rec['species'] = cols[0]
      rec['classification'] = cols[1]
      rec['assessment'] = cols[2]
      rec['authority'] = cols[3]
      data.append(rec)

   return(data)

def getClassifications():
   pid = 464
   raw_html = simple_get(hostname +'?page_id=%s' % pid)
   html = BeautifulSoup(raw_html, 'html.parser')
   body = html.find(class_='entry-content')

   tables = body.find_all(class_="directory")
   #tables = body.find_all('table')

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
         rec['description'] = cols[2]
         data.append(rec)

   return(data)

pages = getTopLevelPage()
#print(pages)
content = []
for page in pages:
   d = getSpeciesPage(page)
   content += d

print(json.dumps(content))


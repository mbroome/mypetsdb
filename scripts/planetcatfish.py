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

hostname = 'https://www.planetcatfish.com'
commonNameLookup = hostname + '/common/common_names.php?language=English&letter='

def getAlphaCommonPage(letter):
   raw_html = simple_get(commonNameLookup + letter)
   html = BeautifulSoup(raw_html.decode('utf-8','ignore'), 'html.parser')
   tbody = html.find(class_='tablerow1').find_parent("table")

   species = []
   for i, row in enumerate(tbody.find_all('tr')):
      #print(':::')
      #print(row)
      #print(':::')

      cols = row.find_all('td')
      #print(cols)

      # [<td class="tablerow1">187. </td>,
      #  <td class="tablerow1"><a href="/Butter_Catfish" onmouseover="">butter catfish</a> </td>,
      #  <td class="tablerow1"><a href="/schilbe_mystus"><em>Schilbe</em> <em>mystus</em></a></td>,
      #  <td class="tablerow1"> (i: 3, k: 0)</td>]
      link = cols[2].select('a')[0].get('href')
      #print(link)
      cols = [ele.text.strip() for ele in cols]
      #print(cols)
      rec = {}
      rec['link'] = hostname + link
      rec['common_name'] = cols[1].lower()
      rec['scientific_name'] = cols[2].replace('(', '').replace(')', '').lower()
      species.append(rec)

   return(species)

c = getAlphaCommonPage("b")
print(json.dumps(c))


import os
import json
import requests
import time

from sqlalchemy import func, or_

from mypetsdb.config import settings

import mypetsdb.models as models

# do a full lookup and build the cache if we found a specific species
def species_lookup(id):
   id = id.lower()
   id = id.rstrip().lstrip()
   
   species = species_cached_lookup(id)

   #print('### here')

   if species:
      #print('already cached species')
      return(species)

   if len(id) < 3:
      return([])

   id = id.replace(' ', '%')

   # first try a fuzzy search on the species name
   species = (models.Session.query(models.SpeciesNameXREF)
                .filter(models.SpeciesNameXREF.scientific_name.ilike('%{0}%'.format(id)))
                .order_by(models.SpeciesNameXREF.scientific_name)
                .limit(50)
                .all())

   # we need to dedup the species list
   recList = {}
   if species:
      #print('@@@ in the species list')
      # the species lookup is effectifly not duplicated already
      for s in species:
         s =  models.PetSpeciesDatum(scientific_name=s.scientific_name)
         c = species_get_common_names(s.scientific_name)
         #v = species_get_variety_names(s.scientific_name)

         recList[s.scientific_name] = {'species': s, 'common': c, 'links': []}

   #print('@@@ in the common list')
   # but we might have more than one common name for the same species
   common = (models.Session.query(models.CommonNameXREF)
             .filter(models.CommonNameXREF.common_name.ilike('%{0}%'.format(id)))
             .limit(50)
             .all())

   if common:
      slist = {}
      for c in common:
         slist[c.scientific_name] = True

      for name in slist:
         s =  models.PetSpeciesDatum(scientific_name=name)
         c = species_get_common_names(name)
         #v = species_get_variety_names(name)

         recList[s.scientific_name] = {'species': s, 'common': c, 'links': []}

   # but we might have more than one common name for the same species
   varieties = (models.Session.query(models.SpeciesVarietyDatum)
                .filter(models.SpeciesVarietyDatum.variety.ilike('%{0}%'.format(id)))
                .limit(50)
                .all())

   if varieties:
      vlist = {}
      vdata = {}
      for v in varieties:
         vlist[v.scientific_name] = True
         if not v.scientific_name in vdata:
            vdata[v.scientific_name] = []
         vdata[v.scientific_name].append(v)

      #print(vlist)
      #print(vdata)
      for name in vlist:
         s =  models.PetSpeciesDatum(scientific_name=name)
         c = species_get_common_names(name)
         #v = species_get_variety_names(name)

         recList[s.scientific_name] = {'species': s, 'common': c, 'varieties': vdata[name], 'links': []}

   #print(recList)
   # since we stuck the data into a dict, we need to turn the values into an array
   response = []
   for r in sorted(recList):
      response.append(recList[r])

   return(response)

def species_get_common_names(id):
   common = (models.Session.query(models.CommonNameXREF)
             .filter(models.CommonNameXREF.scientific_name == id)
             .order_by(models.CommonNameXREF.common_name)
             .all())
   return(common)

def species_get_variety_names(id):
   varieties = (models.Session.query(models.SpeciesVarietyDatum)
             .filter(models.SpeciesVarietyDatum.scientific_name == id)
             .order_by(models.SpeciesVarietyDatum.variety)
             .all())
   return(varieties)

def species_get_planetcatfish(id):
   pcatfish = (models.Session.query(models.PlanetCatfishXREF)
               .filter(models.PlanetCatfishXREF.scientific_name == id)
               .all())
   return(pcatfish)

def species_get_seriouslyfish(id):
   seriouslyfish = (models.Session.query(models.SeriouslyFishXREF)
                    .filter(models.SeriouslyFishXREF.scientific_name == id)
                    .all())
   return(seriouslyfish)

def species_get_links(id):
   links = {}

   #pcatfish = species_get_planetcatfish(id)
   #for pcat in pcatfish:
   #   links[pcat.scientific_name + ':' + 'planetcatfish'] = {'url': pcat.link,
   #                                                          'source': 'planetcatfish'}

   seriouslyfish = species_get_seriouslyfish(id)
   for fish in seriouslyfish:
      links[fish.scientific_name + ':' + 'seriouslyfish'] = {'url': fish.link,
                                                             'source': 'seriouslyfish'}


   return(links.values())

# return a species from our cache if we have it
def species_cached_lookup(id):
   id = id.lower()
   species = (models.Session.query(models.PetSpeciesDatum)
       .filter(models.PetSpeciesDatum.scientific_name == id)
       .first())

   common = species_get_common_names(id)
   varieties = species_get_variety_names(id)
   links = species_get_links(id)

   if species:
      return({'species': species, 'common': common, 'links': links, 'varieties': varieties})



def species_lookup_scientific(id):
   species = species_cached_lookup(id)

   if species:
      return(species)
   else:
      species = (models.Session.query(models.SpeciesNameXREF)
                 .filter(models.SpeciesNameXREF.scientific_name == id)
                 .first())

      if species:
         #print('#### scientific_lookup lookup:')
         #print(species)

         rec = models.PetSpeciesDatum(scientific_name=species.scientific_name)
         rec = species_metadata_callout(rec)
         models.Session.add(rec)
         models.Session.commit()

         common = species_get_common_names(id)
         links = species_get_links(id)

         if rec:
            return({'species': rec, 'common': common, 'links': links})



# lookup a species on the iucn red list
def species_metadata_callout(species):
   start = time.time()
   '''
   token = "a2e02f6727c0a4c8b63144b65b4357ddb1c5f357afb52ca84bf43faf902c9af2"
   url = 'http://apiv3.iucnredlist.org/api/v3/species/%s?token=%s' % (species.scientific_name, token)

   print('metadata lookup callout start: %s' % start)
   #print url
   response = requests.request(
      "GET",
      url,
      timeout=10
   )
   try:
      data = json.loads(response.text)
   except Exception, e:
      print('Error getting data: %s' % url)
      print(response.url)
      print(e)

   try:
      for rec in data['result']:
         species.iucn_id = rec['taxonid']
         species.iucn_category = rec['category']
   except:
      pass
   '''

   iucn = (models.Session.query(models.IUCNRedListXREF)
           .filter(models.IUCNRedListXREF.scientific_name == species.scientific_name)
           .first())

   if iucn:
      species.iucn_category = iucn.category
      species.iucn_link = iucn.link

   cares = (models.Session.query(models.CaresXREF)
            .filter(models.CaresXREF.scientific_name == species.scientific_name)
            .first())

   if cares:
      species.cares_category = cares.category
      species.cares_link = cares.link

   end = time.time()
   print('metadata lookup callout end: %s: took %s seconds' % (end, end - start))
   return(species)

def endangered_classification_map():
   content = open(settings.TOP_LEVEL_DIR + '/data/' + 'classifications.json', 'r').read()
   data = json.loads(content)
   classes = {}
   for c in data:
      classes[c['key'].lower()] = c

   return(classes)


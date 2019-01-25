import os
import json
import requests

from sqlalchemy import func, or_

import mypetsdb.models as models

# return a species from our cache if we have it
def species_cached_lookup(id):
   id = id.lower()
   species = (models.Session.query(models.SpeciesDatum)
       .filter(or_(models.SpeciesDatum.scientific_name == id.lower(), models.SpeciesDatum.common_name == id.lower()))
       .first())
   return(species)

# do a full lookup and build the cache if we found a specific species
def species_lookup(id):
   id = id.lower()
   #species = (models.Session.query(models.SpeciesDatum)
   #    .filter(or_(models.SpeciesDatum.scientific_name == id.lower(), models.SpeciesDatum.common_name == id.lower()))
   #    .first())
   species = species_cached_lookup(id)

   if species:
      print('already cached species')
      return(species)

   # ok, we don't have an existing record so we need to figure out what
   # the user is actually asking for.

   # is it by common name?
   names = (models.Session.query(models.CommonNameDatum)
             .filter(or_(models.CommonNameDatum.common_name.ilike('%{0}%'.format(id)), models.CommonNameDatum.scientific_name.ilike('%{0}%'.format(id))))
             .all())

   if names:
      # if it's one specific match for the name, this 'should' be it
      if len(names) == 1:
         # so we make sure we have the proper scientific name entry
         species = species_metadata_callout(models.SpeciesDatum(scientific_name=names[0].scientific_name.lower()))
         species.common_name = names[0].common_name.lower()
         models.Session.add(species)
         models.Session.commit()

         return(species)

      else: # transform the data to be consistent with our species cache
         response = []
         for c in names:
            rec = models.SpeciesDatum(scientific_name=c.scientific_name,
                                      common_name=c.common_name)
            response.append(rec)
         return(response)

   # return a null
   return(species)

# lookup a species on the iucn red list
def species_metadata_callout(species):
   token = "a2e02f6727c0a4c8b63144b65b4357ddb1c5f357afb52ca84bf43faf902c9af2"
   url = 'http://apiv3.iucnredlist.org/api/v3/species/%s?token=%s' % (species.scientific_name, token)
   #print url
   response = requests.request(
      "GET",
      url
   )
   data = json.loads(response.text)

   try:
      for rec in data['result']:
         species.iucn_id = rec['taxonid']
         species.iucn_category = rec['category']
   except:
      pass

   return(species)


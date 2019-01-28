import os
import json
import requests

from sqlalchemy import func, or_

import mypetsdb.models as models

# return a species from our cache if we have it
def species_cached_lookup(id):
   id = id.lower()
   species = (models.Session.query(models.PetSpeciesDatum)
       .filter(models.PetSpeciesDatum.scientific_name == id.lower())
       .first())
   return(species)

# do a full lookup and build the cache if we found a specific species
def species_lookup(id):
   id = id.lower()
   species = species_cached_lookup(id)

   #print('### here')

   if species:
      print('already cached species')
      return(species)

   species = (models.Session.query(models.SpeciesNameXREF)
                .filter(models.SpeciesNameXREF.scientific_name.ilike('%{0}%'.format(id)))
                .all())

   #print('#### species lookup:')
   #print(species)
   response = []
   for s in species:
      rec =  models.PetSpeciesDatum(scientific_name=s.scientific_name)
      #if len(species) == 1:
      #   rec = species_metadata_callout(rec)
      #   models.Session.add(rec)
      #   models.Session.commit()

      response.append(rec)
   # return a null
   return(response)

def species_lookup_scientific(id):
   species = species_cached_lookup(id)

   if species:
      return(species)
   else:
      species = (models.Session.query(models.SpeciesNameXREF)
                 .filter(models.SpeciesNameXREF.scientific_name == id)
                 .first())

      if species:
         print('#### scientific_lookup lookup:')
         print(species)

         rec = models.PetSpeciesDatum(scientific_name=species.scientific_name)
         rec = species_metadata_callout(rec)
         models.Session.add(rec)
         models.Session.commit()

         return(rec)



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


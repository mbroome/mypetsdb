import os
import json
import requests

from sqlalchemy import func, or_

import mypetsdb.models as models

# return a species from our cache if we have it
def species_cached_lookup(id):
   id = id.lower()
   species = (models.Session.query(models.PetSpeciesDatum)
       .filter(models.PetSpeciesDatum.scientific_name == id)
       .first())

   common = species_get_common_names(id)

   if species:
      return({'species': species, 'common': common})

# do a full lookup and build the cache if we found a specific species
def species_lookup(id):
   id = id.lower()
   id = id.rstrip().lstrip()
   
   species = species_cached_lookup(id)

   #print('### here')

   if species:
      print('already cached species')
      return(species)

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
      print('@@@ in the species list')
      # the species lookup is effectifly not duplicated already
      for s in species:
         s =  models.PetSpeciesDatum(scientific_name=s.scientific_name)
         c = species_get_common_names(s.scientific_name)
         recList[s.scientific_name] = {'species': s, 'common': c}

   print('@@@ in the common list')
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

         recList[s.scientific_name] = {'species': s, 'common': c}

   # since we stuck the data into a dict, we need to turn the values into an array
   response = []
   for r in sorted(recList):
      response.append(recList[r])

   return(response)

def species_get_common_names(id):

   common = (models.Session.query(models.CommonNameXREF)
             .filter(models.CommonNameXREF.scientific_name == id)
             .all())

   return(common)


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

   cares = (models.Session.query(models.CaresXREF)
            .filter(models.CaresXREF.scientific_name == species.scientific_name)
            .first())

   if cares:
      species.cares = cares.code

   return(species)


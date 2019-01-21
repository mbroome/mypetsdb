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
   species = (models.Session.query(models.SpeciesDatum)
       .filter(or_(models.SpeciesDatum.scientific_name == id.lower(), models.SpeciesDatum.common_name == id.lower()))
       .first())
   #species = None

   if species:
      print('already cached species')
      return(species)

   # ok, we don't have an existing record so we need to figure out what
   # the user is actually asking for.

   # is it by common name?
   common = (models.Session.query(models.ITISCommonName)
             .filter(models.ITISCommonName.vernacular_name.ilike('%{0}%'.format(id)))
             .all())

   if common:
      # if it's one specific match for the common name, this 'should' be it
      if len(common) == 1:
         # so we make sure we have the proper scientific name entry
         s = (models.Session.query(models.ITISSpecies)
              .filter(models.ITISSpecies.complete_name == common[0].complete_name)
              .first())

         # found a match to save the record in our local cache
         if s:
            species = species_metadata_callout(models.SpeciesDatum(scientific_name=s.complete_name.lower()))
            species.common_name = common[0].vernacular_name.lower()
            models.Session.add(species)
            models.Session.commit()

            return(species)

         return(s)
      else: # transform the data to be consistent with our species cache
         response = []
         for c in common:
            name = ''
            if not name:
               name = c.vernacular_name.lower()
            if c.language.lower() == 'english':
               name = c.vernacular_name.lower()

            rec = models.SpeciesDatum(scientific_name=c.unit_name1.lower() + " " + c.unit_name2.lower(),
                                      common_name=name)
            #rec = {'common_name': name,
            #       'scientific_name': c.unit_name1.lower() + " " + c.unit_name2.lower(),
            #       'endangered_status': None,
            #       'iucn_category': '',
            #       'iucn_id': None,
            #       'cares': None
            #      }
            response.append(rec)
         return(response)

   else:
      # see if we can find a scientific name match
      sq = (models.Session.query(models.ITISSpecies)
          .filter(models.ITISSpecies.complete_name.ilike('%{0}%'.format(id)))
          .all())

      if sq and len(sq) == 1:
         species = species_metadata_callout(models.SpeciesDatum(scientific_name=sq[0].complete_name.lower()))

         # see if we can find a matching common name
         common = (models.Session.query(models.ITISCommonName)
                   .filter(models.ITISCommonName.complete_name == sq[0].complete_name.lower())
                   .all())

         # This gets a bit hairy since we can have different languages
         # for common names.  So prefer english and fall back to others.
         if common:
            name = ''
            for c in common:
               if not name:
                  name = c.vernacular_name.lower()
               if c.language.lower() == 'english':
                  name = c.vernacular_name.lower()

            species.common_name = name

         # save the species to our local cache
         models.Session.add(species)
         models.Session.commit()

         return(species)

      else:
         response = []
         #print(sq)
         for s in sq:
            newspecies = _scientific_to_common(models.SpeciesDatum(scientific_name=s.complete_name.lower()))
            response.append(newspecies)

         return(response)
   
def _scientific_to_common(species):
   # see if we can find a matching common name
   common = (models.Session.query(models.ITISCommonName)
             .filter(models.ITISCommonName.complete_name == species.scientific_name.lower())
             .all())

   # This gets a bit hairy since we can have different languages
   # for common names.  So prefer english and fall back to others.
   if common:
      name = ''
      for c in common:
         if not name:
            name = c.vernacular_name.lower()
         if c.language.lower() == 'english':
            name = c.vernacular_name.lower()

      species.common_name = name

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


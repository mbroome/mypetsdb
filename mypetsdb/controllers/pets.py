from flask import Flask, request, jsonify, Blueprint
import os
import json
import requests
import time
import datetime

from flask_login import current_user
from sqlalchemy import func, or_

from mypetsdb import ma
import mypetsdb.models as models
import mypetsdb.controllers.species

def _flatten_pet_dict(content):
   data = {}
   # detect if we were passed a flattened object or a nested dict
   if 'pet' in content and 'species' in content:
      data['scientific_name'] = content['species']['scientific_name']
      data['desc'] = content['pet']['desc']
      data['public'] = content['pet']['public']
      data['variant'] = content['pet']['variant']
      data['collection_point'] = content['pet']['collection_point']
      data['start'] = content['pet']['start']
      data['end'] = content['pet']['end']
   else:
      data = content
   return(data)

def pet_search(name):
   q = (models.Session.query(models.PetDatum, models.SpeciesDatum)
        .select_from(models.PetDatum)
        .filter(models.PetDatum.scientific_name == models.SpeciesDatum.scientific_name)
        .filter(or_(models.PetDatum.desc.ilike('%{0}%'.format(name)), models.PetDatum.scientific_name.ilike('%{0}%'.format(name)),  models.SpeciesDatum.common_name.ilike('%{0}%'.format(name))))
        .all())

   response = []
   for row in q:
      notes = (models.Session.query(models.PetNoteDatum)
               .filter(models.PetNoteDatum.pet_id == row[0].pet_id)
               .all())
      #print(notes)

      rec = {"pet": row[0], "species": row[1], "notes": notes}
      response.append(rec)
   return(response)

def pet_lookup_all():
   q = (models.Session.query(models.PetDatum, models.SpeciesDatum)
       .select_from(models.PetDatum)
       .filter(models.PetDatum.scientific_name == models.SpeciesDatum.scientific_name)
       .all())

   #print(q)

   response = []
   for row in q:
      notes = (models.Session.query(models.PetNoteDatum)
               .filter(models.PetNoteDatum.pet_id == row[0].pet_id)
               .all())
      #print(notes)

      rec = {"pet": row[0], "species": row[1], "notes": notes}
      response.append(rec)
   return(response)

def pet_lookup_specific(id):
   #print('@@ get that pet: ' + id)

   q = (models.Session.query(models.PetDatum, models.SpeciesDatum)
       .select_from(models.PetDatum)
       .filter(models.PetDatum.scientific_name == models.SpeciesDatum.scientific_name)
       .filter(models.PetDatum.pet_id == id)
       .first())
   
   notes = (models.Session.query(models.PetNoteDatum)
            .filter(models.PetNoteDatum.pet_id == q[0].pet_id)
            .all())

   pet, species = q
   return({"pet": pet, "species": species, "notes": notes})

def pet_create(content):
   #userid = current_user.username
   #if not userid:
   userid = 'mbroome'
   #print(content)

   data = _flatten_pet_dict(content)

   # find the species data
   species = mypetsdb.controllers.species.species_cached_lookup(data['scientific_name'])

   # make the new pet and save it
   pet = models.PetDatum(
               userid=userid,
               desc=data['desc'],
               public=data['public'],
               scientific_name=data['scientific_name']
            )

   pet.variant = data['variant']
   pet.collection_point = data['collection_point']
   pet.start = data['start']
   pet.end = data['end']


   models.Session.add(pet)
   models.Session.commit()

   return({"pet": pet, "species": species, "notes": []})

def pet_update(id, content):
   userid = 'mbroome'

   data = _flatten_pet_dict(content)

   species = mypetsdb.controllers.species.species_cached_lookup(data['scientific_name'])

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.userid == userid)
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.public = data['public']
   pet.desc = data['desc']

   pet.variant = data['variant']
   pet.collection_point = data['collection_point']
   pet.start = data['start']
   pet.end = data['end']

   models.Session.commit()

   notes = (models.Session.query(models.PetNoteDatum)
            .filter(models.PetNoteDatum.pet_id == pet.pet_id)
            .all())

   return({"pet": pet, "species": species, "notes": notes})

def pet_delete(id):
   userid = 'mbroome'

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.userid == userid)
         .filter(models.PetDatum.pet_id == id)
         .first())

   if pet:
      notes = pet_note_get(id)

      if notes:
         print(notes)
         for note in notes:
            models.Session.delete(note)

      models.Session.delete(pet)
      models.Session.commit()

      return(True)
   return(False)

def pet_start(id):

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.start = datetime.datetime.now()
   models.Session.commit()

   return(pet)

def pet_stop(id):

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.pet_id == id)
         .first())

   #pet.stop = datetime.datetime.now()
   pet.end = datetime.datetime.now()
   models.Session.commit()

   return(pet)

################################################
# notes
def pet_note_get(id):
   notes = (models.Session.query(models.PetNoteDatum)
           .filter(models.PetNoteDatum.pet_id == id)
           .all())

   return(notes)

def pet_note_create(id, content):

   note = models.PetNoteDatum(public=content['public'],
                              note=content['note'],
                              pet_id=id)
   models.Session.add(note)
   models.Session.commit()

   #return(note)
   return(pet_lookup_specific(id))

def pet_note_update(id, note_id, content):

   note = (models.Session.query(models.PetNoteDatum)
           .filter(models.PetNoteDatum.note_id == note_id)
           .first())

   note.public = content['public']
   note.note = content['note']

   models.Session.commit()

   #return(note)
   return(pet_lookup_specific(id))


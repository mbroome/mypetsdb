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
      data['variety'] = content['pet']['variety']
      data['collection_point'] = content['pet']['collection_point']
      data['start'] = content['pet']['start']
      data['end'] = content['pet']['end']
      data['group_name'] = content['pet']['group_name']
   else:
      data = content
   return(data)

def pet_search(name):
   userid = current_user.username

   q = (models.Session.query(models.PetDatum, models.PetSpeciesDatum)
        .select_from(models.PetDatum)
        .filter(models.PetDatum.scientific_name == models.PetSpeciesDatum.scientific_name)
        .filter(or_(models.PetDatum.desc.ilike('%{0}%'.format(name)), models.PetDatum.scientific_name.ilike('%{0}%'.format(name)), models.PetDatum.variety.ilike('%{0}%'.format(name))))
        .filter(models.PetDatum.userid == userid)
        .order_by(models.PetDatum.group_name,models.PetDatum.desc)
        .all())

   response = []
   for row in q:
      notes = (models.Session.query(models.PetNoteDatum)
               .filter(models.PetNoteDatum.pet_id == row[0].pet_id)
               .all())

      common = mypetsdb.controllers.species.species_get_common_names(row[0].scientific_name)

      rec = {"pet": row[0], "species": row[1], "notes": notes, "common": common}
      response.append(rec)
   return(response)

def pet_lookup_all():
   userid = current_user.username

   q = (models.Session.query(models.PetDatum, models.PetSpeciesDatum)
       .select_from(models.PetDatum)
       .filter(models.PetDatum.scientific_name == models.PetSpeciesDatum.scientific_name)
       .filter(models.PetDatum.userid == userid)
       .order_by(models.PetDatum.group_name,models.PetDatum.desc)
       .all())

   #print(q)

   response = []
   for row in q:
      notes = (models.Session.query(models.PetNoteDatum)
               .filter(models.PetNoteDatum.pet_id == row[0].pet_id)
               .all())

      common = mypetsdb.controllers.species.species_get_common_names(row[0].scientific_name)
      links = mypetsdb.controllers.species.species_get_links(row[0].scientific_name)

      rec = {"pet": row[0], "species": row[1], "notes": notes, "common": common, "links": links}
      response.append(rec)
   return(response)

def pet_lookup_specific(id):
   userid = current_user.username
   #print('@@ get that pet: ' + id)

   q = (models.Session.query(models.PetDatum, models.PetSpeciesDatum)
       .select_from(models.PetDatum)
       .filter(models.PetDatum.scientific_name == models.PetSpeciesDatum.scientific_name)
       .filter(models.PetDatum.userid == userid)
       .filter(models.PetDatum.pet_id == id)
       .first())
   
   notes = (models.Session.query(models.PetNoteDatum)
            .filter(models.PetNoteDatum.pet_id == q[0].pet_id)
            .all())

   common = mypetsdb.controllers.species.species_get_common_names(q[0].scientific_name)

   pet, species = q
   return({"pet": pet, "species": species, "notes": notes, "common": common})

def pet_create(content):
   userid = current_user.username
   #print(content)

   data = _flatten_pet_dict(content)

   # find the species data
   species = mypetsdb.controllers.species.species_cached_lookup(data['scientific_name'])

   if not species:
      #print('################ lookup uncached pet')
      species = mypetsdb.controllers.species.species_lookup(data['scientific_name'])
      #print(species)

   # make the new pet and save it
   pet = models.PetDatum(
               userid=userid,
               desc=data['desc'],
               public=data['public'],
               scientific_name=data['scientific_name']
            )

   pet.variety = data['variety']
   pet.collection_point = data['collection_point']
   pet.start = data['start']
   pet.end = data['end']
   pet.group_name = data['group_name']

   models.Session.add(pet)
   models.Session.commit()

   return({"pet": pet, "species": species, "notes": []})

def pet_update(id, content):
   userid = current_user.username

   data = _flatten_pet_dict(content)

   species = mypetsdb.controllers.species.species_cached_lookup(data['scientific_name'])

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.userid == userid)
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.public = data['public']
   pet.desc = data['desc']

   pet.variety = data['variety']
   pet.collection_point = data['collection_point']
   pet.start = data['start']
   pet.end = data['end']
   pet.group_name = data['group_name']

   models.Session.commit()

   notes = (models.Session.query(models.PetNoteDatum)
            .filter(models.PetNoteDatum.pet_id == pet.pet_id)
            .all())

   return({"pet": pet, "species": species, "notes": notes})

def pet_delete(id):
   userid = current_user.username

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
   userid = current_user.username

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.userid == userid)
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.start = datetime.datetime.now()
   models.Session.commit()

   return(pet)

def pet_stop(id):
   userid = current_user.username

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.userid == userid)
         .filter(models.PetDatum.pet_id == id)
         .first())

   #pet.stop = datetime.datetime.now()
   pet.end = datetime.datetime.now()
   models.Session.commit()

   return(pet)

################################################
# notes
def pet_note_get_id(id, note_id):
   userid = current_user.username
   note = (models.Session.query(models.PetNoteDatum)
           .filter(models.PetNoteDatum.pet_id == id)
           .filter(models.PetNoteDatum.note_id == note_id)
           .first())

   return(note)

def pet_note_get(id):
   userid = current_user.username
   notes = (models.Session.query(models.PetNoteDatum)
           .filter(models.PetNoteDatum.pet_id == id)
           .order_by(models.PetNoteDatum.note_id)
           .all())

   return(notes)

def pet_note_create(id, content):
   userid = current_user.username

   note = models.PetNoteDatum(public=content['public'],
                              note=content['note'],
                              pet_id=id)
   models.Session.add(note)
   models.Session.commit()

   #return(note)
   return(pet_lookup_specific(id))

def pet_note_update(id, note_id, content):
   userid = current_user.username

   note = (models.Session.query(models.PetNoteDatum)
           .filter(models.PetNoteDatum.note_id == note_id)
           .first())

   note.public = content['public']
   note.note = content['note']

   models.Session.commit()

   #return(note)
   return(pet_lookup_specific(id))

def pet_note_delete(id, note_id):
   userid = current_user.username

   note = (models.Session.query(models.PetNoteDatum)
           .filter(models.PetNoteDatum.note_id == note_id)
           .first())

   if note:
      models.Session.delete(note)
      models.Session.commit()

   return(True)



from flask import Flask, request, jsonify, Blueprint
import os
import json
import requests
import time
import datetime

from flask_login import current_user

from mypetsdb import ma
import mypetsdb.models as models
import mypetsdb.controllers.species


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
   print('@@ get that pet: ' + id)

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

   # find the species data
   species = mypetsdb.controllers.species.species_cached_lookup(content['scientific_name'])

   # make the new pet and save it
   pet = models.PetDatum(
               userid=userid,
               desc=content['desc'],
               public=content['public'],
               scientific_name=content['scientific_name']
            )

   models.Session.add(pet)
   models.Session.commit()

   return({"pet": pet, "species": species, "notes": []})

def pet_update(id, content):
   userid = 'mbroome'

   species = mypetsdb.controllers.species.species_cached_lookup(content['scientific_name'])

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.userid == userid)
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.public = content['public']
   pet.desc = content['desc']
   models.Session.commit()

   notes = (models.Session.query(models.PetNoteDatum)
            .filter(models.PetNoteDatum.pet_id == pet.pet_id)
            .all())

   #output = pet_schema.dump(pet).data
   #print output
   return({"pet": pet, "species": species, "notes": notes})

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
           .first())

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


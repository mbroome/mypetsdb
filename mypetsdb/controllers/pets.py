from flask import Flask, request, jsonify, Blueprint
import os
import json
import requests
import time
import datetime

from flask_login import current_user

from mypetsdb import ma
import mypetsdb.models as models


def pet_lookup_all():
   q = (models.Session.query(models.PetDatum)
       #.filter(models.PetDatum.pet_id == id)
       .all())

   return(q)

def pet_lookup_specific(id):
   print('@@ get that pet: ' + id)
   q = (models.Session.query(models.PetDatum)
       .filter(models.PetDatum.pet_id == id)
       .first())

   #print(q)
   return(q)

def pet_create(content):
   # see if we already know about the species
   species = (models.Session.query(models.SpeciesDatum)
       .filter(models.SpeciesDatum.scientific_name == content['scientific_name'])
       .first())

   # if we don't know about it, find it and check it's status and store it for later
   if not species:
      species = models.SpeciesDatum(scientific_name=content['scientific_name'])


      token = "a2e02f6727c0a4c8b63144b65b4357ddb1c5f357afb52ca84bf43faf902c9af2"
      url = 'http://apiv3.iucnredlist.org/api/v3/species/%s?token=%s' % (content['scientific_name'], token)
      #print url
      response = requests.request(
         "GET",
         url
      )
      data = json.loads(response.text)
      #print data
      for rec in data['result']:
         species.iucn_id = rec['taxonid']
         species.iucn_category = rec['category']

      models.Session.add(species)
      models.Session.commit()


   # make the new pet and save it
   pet = models.PetDatum(
               userid=current_user.username,
               description=content['description'],
               public=content['public']
            )

   models.Session.add(pet)
   models.Session.commit()

   pet.species.append(species)
   models.Session.commit()

   return(pet)

def pet_update(id, content):
   species = (models.Session.query(models.SpeciesDatum)
       .filter(models.SpeciesDatum.scientific_name == content['scientific_name'])
       .first())

   if not species:
      species = models.SpeciesDatum(
         scientific_name=content['scientific_name'])


      token = "a2e02f6727c0a4c8b63144b65b4357ddb1c5f357afb52ca84bf43faf902c9af2"
      url = 'http://apiv3.iucnredlist.org/api/v3/species/%s?token=%s' % (content['scientific_name'], token)
      #print url
      response = requests.request(
         "GET",
         url
      )
      data = json.loads(response.text)
      #print data
      for rec in data['result']:
         species.iucn_id = rec['taxonid']
         species.iucn_category = rec['category']

      models.Session.add(species)
      models.Session.commit()



   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.userid == current_user.username)
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.public = content['public']
   pet.description = content['description']

   pet.species.append(species)
   models.Session.commit()

   #output = pet_schema.dump(pet).data
   #print output
   return(pet)

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

def pet_note_create(id, content):
   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.pet_id == id)
         .first())

   if not pet:
      return(None)

   note = models.PetNote(public=content['public'],
                         note=content['note'])
   pet.notes.append(note)
   models.Session.commit()

   return(pet)

def pet_note_update(id, note_id, content):

   note = (models.Session.query(models.PetNote)
         .filter(models.PetNote.note_id == note_id)
         .first())

   note.public = content['public']
   note.note = content['note']

   models.Session.commit()

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.pet_id == id)
         .first())

   return(pet)


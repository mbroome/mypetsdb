from flask import Flask, request, jsonify, Blueprint
import os
import json
import requests
import time
import datetime

from mypetsdb import ma
import mypetsdb.models as models

class PetSchema(ma.ModelSchema):
   class Meta:
      model = models.PetDatum
   notes = ma.Nested('PetNoteSchema', many=True)
   species = ma.Nested('SpeciesSchema', many=True)

class SpeciesSchema(ma.ModelSchema):
   class Meta:
      model = models.SpeciesDatum

class PetNoteSchema(ma.ModelSchema):
   class Meta:
      model = models.PetNote

pet_schema = PetSchema(strict=True)
pets_schema = PetSchema(many=True, strict=True)

# define the routes
routes = Blueprint('pets', __name__, url_prefix='/pets')

# Get all pets for a given user
@routes.route("/mypets", methods=["GET"])
def pet_lookup_all():
   q = (models.Session.query(models.PetDatum)
       #.filter(models.PetDatum.pet_id == id)
       .all())

   return(pets_schema.jsonify(q))

# get a specific pet for a given user
@routes.route("/mypets/<id>", methods=["GET"])
def pet_lookup_specific(id):
   q = (models.Session.query(models.PetDatum)
       .filter(models.PetDatum.pet_id == id)
       .first())

   return(pet_schema.jsonify(q))

# Create a new pet for a given user
@routes.route("/mypets", methods=["POST"])
def pet_create():
   content = request.get_json()
   in_genus, in_species = content['scientific_name'].split(' ')

   # see if we already know about the species
   species = (models.Session.query(models.SpeciesDatum)
       .filter(models.SpeciesDatum.scientific_name == content['scientific_name'])
       .first())

   # if we don't know about it, find it and check it's status and store it for later
   if not species:
      species = models.SpeciesDatum(
         scientific_name=content['scientific_name'],
         genus=in_genus,
         species=in_species)


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
               userid=content['userid'],
               description=content['description'],
               public=content['public']
            )

   models.Session.add(pet)
   models.Session.commit()

   pet.species.append(species)
   models.Session.commit()

   return(pet_schema.jsonify(pet))

# Update an existing pet for a given user
@routes.route("/mypets/<id>", methods=["POST"])
def pet_update(id):
   content = request.get_json()
   in_genus, in_species = content['scientific_name'].split(' ')

   species = (models.Session.query(models.SpeciesDatum)
       .filter(models.SpeciesDatum.scientific_name == content['scientific_name'])
       .first())

   if not species:
      species = models.SpeciesDatum(
         scientific_name=content['scientific_name'],
         genus=in_genus,
         species=in_species)


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
         .filter(models.PetDatum.userid == content['userid'])
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.public = content['public']
   pet.description = content['description']

   pet.species.append(species)
   models.Session.commit()

   #output = pet_schema.dump(pet).data
   #print output
   return(pet_schema.jsonify(pet))

# start keeping a pet
@routes.route("/mypets/<id>/start", methods=["GET"])
def pet_start(id):

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.pet_id == id)
         .first())

   pet.start = datetime.datetime.now()
   models.Session.commit()

   return(pet_schema.jsonify(pet))

# stop keeping a pet
@routes.route("/mypets/<id>/stop", methods=["GET"])
def pet_stop(id):

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.pet_id == id)
         .first())

   #pet.stop = datetime.datetime.now()
   pet.end = datetime.datetime.now()
   models.Session.commit()

   return(pet_schema.jsonify(pet))

@routes.route("/mypets/<id>/note", methods=["POST"])
def pet_note_update(id):
   content = request.get_json()
   print(content)

   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.pet_id == id)
         .first())

   if not pet:
      return(jsonify({"status": "not found"}))

   note = models.PetNote(public=content['public'],
                         note=content['note'])
   pet.notes.append(note)
   models.Session.commit()

   
   #output = pet_schema.dump(pet).data
   #print output
   return(pet_schema.jsonify(pet))


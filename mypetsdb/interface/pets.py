from flask import Flask, request, jsonify, Blueprint
import os
import json
import requests
import time
import datetime

from marshmallow import Schema, fields, ValidationError, pre_load

import models
import controllers.pets


class PetDatumSchema(Schema):
   class Meta:
      model = models.PetDatum

class PetSpeciesDatumSchema(Schema):
   class Meta:
      model = models.PetSpeciesDatum

class PetNoteDatumSchema(Schema):
   class Meta:
      model = models.PetNoteDatum

class PetSchema(Schema):
   pet = fields.Nested('PetDatumSchema')
   species = fields.Nested('PetSpeciesDatumSchema')
   notes = fields.Nested('PetNoteDatumSchema', many=True)

pet_schema = PetSchema(strict=True)
pets_schema = PetSchema(many=True, strict=True)

note_schema = PetNoteDatumSchema(strict=True)
notes_schema = PetNoteDatumSchema(many=True, strict=True)

# define the routes
routes = Blueprint('pets', __name__, url_prefix='/api/pets')

# Get all pets for a given user
@routes.route("/mypets", methods=["GET"])
def pet_lookup_all():
   pets = controllers.pets.pet_lookup_all()

   #print(pets)
   return(pets_schema.jsonify(pets))

# get a specific pet for a given user
@routes.route("/mypets/<id>", methods=["GET"])
def pet_lookup_specific(id):
   pet = controllers.pets.pet_lookup_specific(id)

   #print(pet['pet'].__dict__)
   #print(pet['species'].__dict__)
   return(pet_schema.jsonify(pet))

# Create a new pet for a given user
@routes.route("/mypets", methods=["POST"])
def pet_create():
   content = request.get_json()
   pet = controllers.pets.pet_create(content)

   print(pet)
   return(pet_schema.jsonify(pet))

# Update an existing pet for a given user
@routes.route("/mypets/<id>", methods=["POST"])
def pet_update(id):
   content = request.get_json()
   pet = controllers.pets.pet_update(id, content)

   print(pet)
   #return({})
   return(pet_schema.jsonify(pet))

# start keeping a pet
@routes.route("/mypets/<id>/start", methods=["GET"])
def pet_start(id):
   pet = controllers.pets.pet_start(id)

   print(pet)
   return({})
#   return(pet_schema.jsonify(pet))

# stop keeping a pet
@routes.route("/mypets/<id>/stop", methods=["GET"])
def pet_stop(id):
   pet = controllers.pets.pet_stop(id)

   print(pet)
   return({})
#   return(pet_schema.jsonify(pet))


###########################################################
# notes
@routes.route("/mypets/<id>/note", methods=["POST"])
def pet_note_create(id):
   content = request.get_json()
   pet = controllers.pets.pet_note_create(id, content)

   return(pet_schema.jsonify(pet))

@routes.route("/mypets/<id>/note/<note_id>", methods=["POST"])
def pet_note_update(id, note_id):
   content = request.get_json()
   pet = controllers.pets.pet_note_update(id, note_id, content)

   return(pet_schema.jsonify(pet))


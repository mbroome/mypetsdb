from flask import Flask, request, jsonify, Blueprint
import os
import json
import requests
import time
import datetime

from mypetsdb import ma
import mypetsdb.models as models
import mypetsdb.controllers.pets

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
routes = Blueprint('pets', __name__, url_prefix='/api/pets')

# Get all pets for a given user
@routes.route("/mypets", methods=["GET"])
def pet_lookup_all():
   q = mypetsdb.controllers.pets.pet_lookup_all()

   return(pets_schema.jsonify(q))

# get a specific pet for a given user
@routes.route("/mypets/<id>", methods=["GET"])
def pet_lookup_specific(id):
   pet = mypetsdb.controllers.pets.pet_lookup_specific(id)

   return(pet_schema.jsonify(pet))

# Create a new pet for a given user
@routes.route("/mypets", methods=["POST"])
def pet_create():
   content = request.get_json()
   pet = mypetsdb.controllers.pets.pet_create(content)

   return(pet_schema.jsonify(pet))

# Update an existing pet for a given user
@routes.route("/mypets/<id>", methods=["POST"])
def pet_update(id):
   content = request.get_json()
   pet = mypetsdb.controllers.pets.pet_update(id, content)

   return(pet_schema.jsonify(pet))

# start keeping a pet
@routes.route("/mypets/<id>/start", methods=["GET"])
def pet_start(id):
   pet = mypetsdb.controllers.pet_start(id)

   return(pet_schema.jsonify(pet))

# stop keeping a pet
@routes.route("/mypets/<id>/stop", methods=["GET"])
def pet_stop(id):
   pet = mypetsdb.controllers.pet_stop(id)

   return(pet_schema.jsonify(pet))

@routes.route("/mypets/<id>/note", methods=["POST"])
def pet_note_create(id):
   content = request.get_json()
   pet = mypetsdb.controllers.pet_note_create(id, content)

   return(pet_schema.jsonify(pet))

@routes.route("/mypets/<id>/note/<note_id>", methods=["POST"])
def pet_note_update(id, note_id):
   content = request.get_json()
   pet = mypetsdb.controllers.pet_note_update(id, note_id, content)

   return(pet_schema.jsonify(pet))


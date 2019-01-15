from flask import Flask, request, jsonify, Blueprint
import os
import json
import requests

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

pet_schema = PetSchema()

# define the routes
routes = Blueprint('pets', __name__, url_prefix='/pets')

@routes.route("/<id>", methods=["GET"])
def pet_lookup(id):
   q = (models.Session.query(models.PetDatum)
       .filter(models.PetDatum.pet_id == id)
       .first())

   print(q.notes[0].note)
   print(q.species[0].iucn_id)
   #output = pet_schema.dump(q).data
   #print(output)
   return(pet_schema.jsonify(q))

@routes.route("/<id>", methods=["POST"])
def pet_update(id):
   content = request.get_json()

   s = 'neolamprologus multifasciatus'
   email = 'mitchell.broome@gmail.com'
   email = 'bob.broome@gmail.com'
   
   species = (models.Session.query(models.SpeciesDatum)
       .filter(models.SpeciesDatum.scientific_name == s)
       .first())

   if not species:
      species = models.SpeciesDatum(
         scientific_name=s,
         genus='neolamprologus',
         species='multifasciatus')


      token = "a2e02f6727c0a4c8b63144b65b4357ddb1c5f357afb52ca84bf43faf902c9af2"
      url = 'http://apiv3.iucnredlist.org/api/v3/species/%s?token=%s' % (s, token)
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
         .filter(models.PetDatum.userid == email)
         .first())

   if not pet:
      pet = models.PetDatum(
                  #scientific_name='neolamprologus multifasciatus',
                  userid=email,
                  public=False
               )

      models.Session.add(pet)
      models.Session.commit()

   pet.species.append(species)
   models.Session.commit()

   output = pet_schema.dump(pet).data
   print output
   return(pet_schema.jsonify(pet))

@routes.route("/<id>/note", methods=["POST"])
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

   
   output = pet_schema.dump(pet).data
   print output
   return(pet_schema.jsonify(pet))


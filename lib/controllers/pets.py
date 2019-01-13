from flask import Flask, request, jsonify, Blueprint
from flask_marshmallow import Marshmallow
import os
import json
import requests

from lib.app import ma
from lib import models


# define the response schema for json output
class PetSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('pet_id', 'scientific_name', 'variant', 'collection_point', 'userid', 'start', 'end', 'description', 'public')
pet_schema = PetSchema()
pets_schema = PetSchema(many=True)

class PetNoteSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('note_id', 'pet_id', 'public', 'note', 'timestamp')

petnote_schema = PetNoteSchema()
petnotes_schema = PetNoteSchema(many=True)


class SpeciesSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('scientific_name', 'common_name', 'endangered_status', 'iucn_category', 'iucn_id', 'cares', 'genus', 'species')

species_schema = SpeciesSchema()
speciess_schema = SpeciesSchema(many=True)


# define the routes
routes = Blueprint('pets', __name__, url_prefix='/pets')

@routes.route("/<id>", methods=["GET"])
def pet_lookup(id):
   q = (models.Session.query(models.PetDatum)
       .filter(models.PetDatum.pet_id == id)
       .all())

   return(pets_schema.jsonify(q))

@routes.route("/<id>", methods=["POST"])
def pet_update(id):
   s = 'neolamprologus multifasciatus'
   email = 'mitchell.broome@gmail.com'
   email = 'bob.broome@gmail.com'
   
   pet = (models.Session.query(models.PetDatum)
         .filter(models.PetDatum.scientific_name == s)
         .filter(models.PetDatum.userid == email)
         .first())

   if not pet:
      pet = models.PetDatum(
                  scientific_name='neolamprologus multifasciatus',
                  userid=email,
                  public=False
               )

      models.Session.add(pet)
      models.Session.commit()


   q = (models.Session.query(models.SpeciesDatum)
       .filter(models.SpeciesDatum.scientific_name == s)
       .first())
   if q:
      return(species_schema.jsonify(q))
   else:
      species = models.SpeciesDatum(
         scientific_name=s,
         genus='neolamprologus',
         species='multifasciatus')


      token = "a2e02f6727c0a4c8b63144b65b4357ddb1c5f357afb52ca84bf43faf902c9af2"
      url = 'http://apiv3.iucnredlist.org/api/v3/species/%s?token=%s' % (s, token)
      print url
      response = requests.request(
         "GET",
         url
      )
      data = json.loads(response.text)
      print data
      for rec in data['result']:
         species.iucn_id = rec['taxonid']
         species.iucn_category = rec['category']

      models.Session.add(species)
      models.Session.commit()

   return("test")
   #return(pet_schema.jsonify(pet))


from flask import Flask, request, jsonify, Blueprint
import os
import json

from marshmallow import Schema, fields, ValidationError, pre_load

#import app
import models
import controllers.species

# define the response schema for json output
class SpeciesSchema(Schema):
   class Meta:
      fields = ('scientific_name','iucn_category','iucn_id','cares_category', 'cares_link', 'planetcatfish_link')

species_schema = SpeciesSchema(strict=True, partial=True)
speciess_schema = SpeciesSchema(many=True, strict=True, partial=True)


# define the routes
routes = Blueprint('species', __name__, url_prefix='/api/species')

# endpoint to handle species lookups
@routes.route("/<id>", methods=["GET"])
def species_q(id):
   q =  controllers.species.species_lookup(id)
   #print(q)
   try:
      return(speciess_schema.jsonify(q))
   except:
      return(species_schema.jsonify(q))


from flask import Flask, request, jsonify, Blueprint
import os
import json

from mypetsdb import ma
import mypetsdb.models as models
import mypetsdb.controllers.species

# define the response schema for json output
class ITISSpeciesSchema(ma.Schema):
   class Meta:
      fields = ('tsn','vernacular_name','unit_name1','unit_name2','complete_name')

itisspecies_schema = ITISSpeciesSchema(strict=True, partial=True)
itisspeciess_schema = ITISSpeciesSchema(many=True, strict=True, partial=True)


# define the routes
routes = Blueprint('species', __name__, url_prefix='/api/species')

# endpoint to handle species lookups
@routes.route("/<id>", methods=["GET"])
def species_q(id):
   q =  mypetsdb.controllers.species.species_lookup(id)
   return(itisspeciess_schema.jsonify(q))



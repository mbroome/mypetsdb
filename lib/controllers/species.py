from flask import Flask, request, jsonify, Blueprint
from flask_marshmallow import Marshmallow
import os
import json

from lib.app import ma
from lib import models

# define the response schema for json output
class ITISCommonNameSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('tsn', 'vernacular_name','unit_name1','unit_name2','complete_name')
itiscommonname_schema = ITISCommonNameSchema()
itiscommonnames_schema = ITISCommonNameSchema(many=True)

class ITISSpeciesSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('tsn', 'unit_name1','unit_name2','complete_name')
itisspecies_schema = ITISSpeciesSchema()
itisspeciess_schema = ITISSpeciesSchema(many=True)


# define the routes
mod_species = Blueprint('species', __name__, url_prefix='/species')

# endpoint to handle species lookups
@mod_species.route("/<id>", methods=["GET"])
def species_lookup(id):
   q = (models.mysession.query(models.ITISCommonName)
       .filter(models.ITISCommonName.vernacular_name.ilike('%{0}%'.format(id)))
       .all())

   if q:
      return(itiscommonnames_schema.jsonify(q))
   else:
      q = (models.mysession.query(models.ITISSpecies)
          .filter(models.ITISSpecies.complete_name.ilike('%{0}%'.format(id)))
          .all())
      return(itisspeciess_schema.jsonify(q))
   


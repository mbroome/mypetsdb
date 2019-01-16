from flask import Flask, request, jsonify, Blueprint
import os
import json

from mypetsdb import ma
import mypetsdb.models as models

# define the response schema for json output
class ITISCommonNameSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('tsn', 'vernacular_name','unit_name1','unit_name2','complete_name')
itiscommonname_schema = ITISCommonNameSchema(strict=True)
itiscommonnames_schema = ITISCommonNameSchema(many=True, strict=True)

class ITISSpeciesSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('tsn', 'unit_name1','unit_name2','complete_name')
itisspecies_schema = ITISSpeciesSchema(strict=True)
itisspeciess_schema = ITISSpeciesSchema(many=True, strict=True)


# define the routes
routes = Blueprint('species', __name__, url_prefix='/species')

# endpoint to handle species lookups
@routes.route("/<id>", methods=["GET"])
def species_lookup(id):
   q = (models.Session.query(models.ITISCommonName)
       .filter(models.ITISCommonName.vernacular_name.ilike('%{0}%'.format(id)))
       .all())

   if q:
      return(itiscommonnames_schema.jsonify(q))
   else:
      q = (models.Session.query(models.ITISSpecies)
          .filter(models.ITISSpecies.complete_name.ilike('%{0}%'.format(id)))
          .all())
      return(itisspeciess_schema.jsonify(q))
   


#from flask import Flask, request, jsonify, Blueprint
import os
import json

#from mypetsdb import ma
import mypetsdb.models as models

def species_lookup(id):
   q = (models.Session.query(models.ITISCommonName)
       .filter(models.ITISCommonName.vernacular_name.ilike('%{0}%'.format(id)))
       .all())

   if not q:
      q = (models.Session.query(models.ITISSpecies)
          .filter(models.ITISSpecies.complete_name.ilike('%{0}%'.format(id)))
          .all())
   return(q)
   


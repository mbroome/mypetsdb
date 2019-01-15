import os

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow

ma = Marshmallow()

def create_app(test_config=None):

   app = Flask(__name__)
   ma.init_app(app)

   import controllers.species
   import controllers.pets

   # Register blueprint(s)
   app.register_blueprint(controllers.species.routes)
   app.register_blueprint(controllers.pets.routes)

   return(app)


import os
import urllib

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from werkzeug.contrib.fixers import ProxyFix


ma = Marshmallow()
#bootstrap = Bootstrap()
bootstrap = None
login_manager = LoginManager()

def create_app(test_config=None):

   app = Flask(__name__)
   app.wsgi_app = ProxyFix(app.wsgi_app)
   ma.init_app(app)
   #bootstrap.init_app(app)
   bootstrap = Bootstrap(app)
   login_manager.init_app(app)

   app.jinja_env.filters['quote_plus'] = lambda u: urllib.quote_plus(u)
   app.jinja_env.filters['hash_key'] = lambda u: abs(hash(u))

   app.config['SECRET_KEY'] = '7c2a2b8a-5936-4a1a-816d-0ac526f8d7ed'

   import interface.species
   import interface.pets
   import interface.ui

   # Register blueprint(s)
   app.register_blueprint(interface.species.routes)
   app.register_blueprint(interface.pets.routes)
   app.register_blueprint(interface.ui.routes)

   return(app)


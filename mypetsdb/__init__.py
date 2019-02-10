import os
import urllib
import json

from flask import Flask, request, render_template, redirect, url_for, Blueprint, flash

from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from werkzeug.contrib.fixers import ProxyFix
from itsdangerous import URLSafeTimedSerializer

import mypetsdb.controllers.utils

ma = Marshmallow()
bootstrap = None
login_manager = LoginManager()
config = mypetsdb.controllers.utils.loadConfig()
ts = URLSafeTimedSerializer(config['flask']['SECRET_KEY'])

def create_app(test_config=None):
   app = Flask(__name__)
   for k in config['flask']:
      app.config[k] = config['flask'][k]

   app.wsgi_app = ProxyFix(app.wsgi_app)
   ma.init_app(app)
   bootstrap = Bootstrap(app)
   login_manager.init_app(app)

   app.jinja_env.filters['quote_plus'] = lambda u: urllib.quote_plus(u)
   app.jinja_env.filters['hash_key'] = lambda u: abs(hash(u))

   import interface.species
   import interface.pets
   import interface.ui
   import interface.auth
   import interface.profile
   import interface.search

   # Register blueprint(s)
   app.register_blueprint(interface.species.routes)
   app.register_blueprint(interface.pets.routes)
   app.register_blueprint(interface.ui.routes)
   app.register_blueprint(interface.auth.routes)
   app.register_blueprint(interface.profile.routes)
   app.register_blueprint(interface.search.routes)



   @app.errorhandler(500)
   def page_not_found(e):
      return render_template('error.html'), 500

   return(app)


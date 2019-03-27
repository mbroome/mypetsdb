import os
import urllib
import json
import logging

from flask import Flask, request, render_template, redirect, url_for, Blueprint, flash

from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from werkzeug.contrib.fixers import ProxyFix
from itsdangerous import URLSafeTimedSerializer

import models
from config import settings

logging.basicConfig()
logger = logging.getLogger(__name__)

import interface.species
import interface.pets
import interface.ui
import interface.auth
import interface.profile
import interface.search

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY

ma = Marshmallow()
login_manager = LoginManager()
ts = URLSafeTimedSerializer(settings.SECRET_KEY)


app.wsgi_app = ProxyFix(app.wsgi_app)
ma.init_app(app)
bootstrap = Bootstrap(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.jinja_env.filters['quote_plus'] = lambda u: urllib.quote_plus(u)
app.jinja_env.filters['hash_key'] = lambda u: abs(hash(u))

# Register blueprint(s)
app.register_blueprint(interface.species.routes)
app.register_blueprint(interface.pets.routes)
app.register_blueprint(interface.ui.routes)
app.register_blueprint(interface.auth.routes)
app.register_blueprint(interface.profile.routes)
app.register_blueprint(interface.search.routes)


@login_manager.user_loader
def load_user(user_id):
   return (models.Session.query(models.User)
            .filter(models.User.id == user_id)
            .first())


@app.errorhandler(500)
def page_not_found(e):
   return render_template('error.html'), 500


@app.teardown_appcontext
def remove_session(exception=None):
   try:
      #print('removing db session')
      models.Session.remove()
   except:
      pass


if __name__ == '__main__':
   logger.setLevel(logging.DEBUG)
   app.run(host='0.0.0.0', debug=True)


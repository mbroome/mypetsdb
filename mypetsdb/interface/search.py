import json

from flask import Flask, request, render_template, redirect, url_for, Blueprint, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import controllers.pets 
import controllers.species
import models
import forms

routes = Blueprint('search', __name__, template_folder='templates', static_folder='static')


#########################################################
# Species search from the main dashboard
@routes.route('/search/species', methods=['GET', 'POST'])
@login_required
def search_species():
   searchform = forms.SearchForm(request.form)
   petform = forms.PetSpeciesDatumForm()
   #print(petform.speciessearch.data)
   q = []
   if request.method == 'POST' and searchform.speciessearch.data:
      #print('get it on')
      q =  controllers.species.species_lookup(searchform.speciessearch.data)
      #print(q)
      if type(q) is not list:
         q = [q]

   return render_template('search/species_search.html', name=current_user.username, searchdata=q, form=petform, searchform=searchform)

# Species details search
@routes.route('/search/species/<id>', methods=['GET'])
@routes.route('/search/species/<id>/variety/<variety>', methods=['GET'])
@login_required
def species_details_search(id, variety=''):
   petform = forms.SpeciesSearchForm()
   #print('variety: ' + variety)

   q =  controllers.species.species_lookup_scientific(id)
   #print(q['species'])
   classes =  controllers.species.endangered_classification_map()
   return render_template('search/search_details.html', name=current_user.username, searchdata=q, form=petform, classifications=classes, variety=variety)


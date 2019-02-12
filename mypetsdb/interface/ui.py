import json

from flask import Flask, request, render_template, redirect, url_for, Blueprint, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from mypetsdb import login_manager, ma
import mypetsdb.controllers.pets 
import mypetsdb.controllers.species
import mypetsdb.models as models
import mypetsdb.forms as forms

login_manager.login_view = 'auth.login'

routes = Blueprint('ui', __name__, template_folder='templates', static_folder='static')


@routes.route('/')
def index():
   if current_user:
      try:
         if current_user.username:
            return redirect(url_for('ui.dashboard'))
      except:
         pass

   return render_template('index.html')

#########################################################
# The base logged in dashboard
@routes.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
   #print(request.data)
   searchform = forms.SearchForm()
   petform = forms.PetForm()

   if request.method == 'POST' and searchform.petsearch.data:
      #print(searchform.petsearch.data)
      p = mypetsdb.controllers.pets.pet_search(searchform.petsearch.data)
   else:
      p = mypetsdb.controllers.pets.pet_lookup_all()

   classifications =  mypetsdb.controllers.species.endangered_classification_map()
   classes = {}
   for c in classifications:
      classes[c.code] = c.name

   return render_template('dashboard.html', name=current_user.username, petdata=p, form=petform, searchform=searchform, classifications=classes)

'''
# Species search from the main dashboard
@routes.route('/dashboard/species', methods=['GET', 'POST'])
@login_required
def dashboard_species():
   searchform = forms.SearchForm()
   speciesform = forms.PetSpeciesDatumForm()
   #print(searchform.speciessearch.data)
   q = None
   if request.method == 'POST' and searchform.speciessearch.data:
      #print('get it on')
      q =  mypetsdb.controllers.species.species_lookup(searchform.speciessearch.data)
      #print(q)
      if type(q) is not list:
         q = [q]

   return render_template('search/species_search.html', name=current_user.username, searchdata=q, form=speciesform, searchform=searchform)

# Species details search
@routes.route('/dashboard/species/<id>', methods=['GET'])
@routes.route('/dashboard/species/<id>/variety/<variety>', methods=['GET'])
@login_required
def species_details_search(id, variety=''):
   speciesform = forms.PetSpeciesDatumForm()
   print('variety: ' + variety)

   q =  mypetsdb.controllers.species.species_lookup_scientific(id)
   #print(q)
   classifications =  mypetsdb.controllers.species.endangered_classification_map()
   classes = {}
   for c in classifications:
      classes[c.code] = c.name
   return render_template('search/search_details.html', name=current_user.username, searchdata=q, form=speciesform, classifications=classes, variety=variety)
'''

############################################################
# manage a specific note about a specific pet
@routes.route('/pet/manage/<id>/note/<note_id>', methods = ['GET', 'POST'])
@login_required
def manage_specific_pet_note_id(id, note_id):
   #print('In dat note edit')
   searchform = forms.SearchForm()
   form = forms.NoteDatumForm(request.form)
   #print(request.form)
   #print(form.data)
   #print('id: %s, note: %s' % (id, note_id))
   if request.method == 'POST':
      if not form.validate_on_submit():
         flash(form.errors, 'danger')
         #print(form.errors)

      if form.submit.data == True:
         status = mypetsdb.controllers.pets.pet_note_update(id, note_id, form.data)
      elif form.delete.data == True:
         #print('## we got a note delete for: %s => %s' % (id, note_id))
         status = mypetsdb.controllers.pets.pet_note_delete(id, note_id)
      return redirect(url_for('ui.dashboard'))
   elif request.method == 'GET':
      #print('in the get')
      note = mypetsdb.controllers.pets.pet_note_get_id(id, note_id)
      #print(note)
      #print(note.__dict__)
      form = forms.NoteDatumForm(obj=note)
      #print(form.data)
      return render_template('manage_note.html', name=current_user.username, form=form, searchform=searchform, pet_id=id, notedata=note)


# manage notes about a specific pet
@routes.route('/pet/manage/<id>/note', methods = ['GET', 'POST'])
@login_required
def manage_specific_pet_note(id):
   searchform = forms.SearchForm()
   form = forms.NoteDatumForm(request.form)
   #print(request.form)
   #print(json.dumps(form.data))
   if request.method == 'POST':
      if not form.validate_on_submit():
         flash(form.errors, 'danger')
         #print(form.errors)
         return render_template('manage_note.html', name=current_user.username, form=form, searchform=searchform, pet_id=id)

      if form.submit.data == True:
         status = mypetsdb.controllers.pets.pet_note_create(id, form.data)
      #elif form.edit.data == True:
      #   #print('### got a note edit request')
      return redirect(url_for('ui.dashboard'))
   elif request.method == 'GET':
      return render_template('manage_note.html', name=current_user.username, form=form, searchform=searchform, pet_id=id)

############################################################
# manage a specific pet
@routes.route('/pet/manage/<id>', methods = ['GET', 'POST'])
@login_required
def manage_specific_pet(id):
   searchform = forms.SearchForm()
   form = forms.PetForm(request.form)
   print(request.form)
   print(request.method)
   #print(json.dumps(form.data))
   if request.method == 'POST':

      #if not form.validate_on_submit():
      #   flash(form.errors, 'danger')
      #   #print(form.errors)

      if form.edit.data == True:
         pet = mypetsdb.controllers.pets.pet_lookup_specific(id)
         editForm = forms.PetForm(pet=pet['pet'], species=pet['species'], notes=[])

         return render_template('manage_pet.html', name=current_user.username, petdata=pet, form=editForm, searchform=searchform)
      elif form.submit.data == True:
         pet = mypetsdb.controllers.pets.pet_update(id, form.data)
      elif form.cancel.data == True:
         return redirect(url_for('ui.dashboard'))
      elif form.delete.data == True:
         status = mypetsdb.controllers.pets.pet_delete(id)
      elif form.note.data == True:
         return redirect(url_for('ui.manage_specific_pet_note', id=id))
      return redirect(url_for('ui.dashboard'))
   elif request.method == 'GET':
      pet = mypetsdb.controllers.pets.pet_lookup_specific(id)
      editForm = forms.PetForm(pet=pet['pet'], species=pet['species'], notes=[])
      return render_template('manage_pet.html', name=current_user.username,  petdata=pet, form=editForm, searchform=searchform)


# create a pet
@routes.route('/pet/manage', methods = ['GET', 'POST'])
@login_required
def manage_pet():
   #print(request.form)
   searchform = forms.SearchForm()
   form = forms.PetForm(request.form)

   if form.csrf_token.data:
      form.pet.csrf_token.data = form.csrf_token.data
      form.species.csrf_token.data = form.csrf_token.data

   #print(request.form)
   #print(json.dumps(form.data))
   if request.method == 'POST':
      if not form.validate_on_submit():
         flash(form.errors, 'danger')
         #print(form.errors)
         #print('failed validation')
      #print(form.species.scientific_name.data)

      #print(form.pet)

      q =  mypetsdb.controllers.species.species_lookup_scientific(form.species.scientific_name.data)

      if form.submit.data == True:
         pet = mypetsdb.controllers.pets.pet_create(form.data)

         return redirect(url_for('ui.dashboard'))
      return render_template('manage_pet.html', name=current_user.username, form=form, searchform=searchform)
   else:
      #print('manage GET')
      return render_template('manage_pet.html', name=current_user.username, form=form, searchform=searchform)


@routes.route('/help')
def help():
   searchform = forms.SearchForm()
   petform = forms.PetForm()

   return render_template('help.html', name=current_user.username, petdata={}, form=petform, searchform=searchform)


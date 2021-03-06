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

@routes.route('/healthcheck')
def healthcheck():
   return("OK")



#########################################################
# The base logged in dashboard
@routes.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
   #print(request.data)
   searchform = forms.SearchForm()
   petform = forms.PetForm()
   pets = []

   if request.method == 'POST' and searchform.petsearch.data:
      #print(searchform.petsearch.data)
      pets = controllers.pets.pet_search(searchform.petsearch.data)
   else:
      pets = controllers.pets.pet_lookup_all()

   petGroups = {}
   for pet in pets:
      # make a placeholder group in the case where someone has
      # not defined groups on pets
      groupName = 'ZZZ__NONE__'
      if pet['pet'].group_name:
         groupName = pet['pet'].group_name
      #print('group name: %s' % groupName)
      if not petGroups.has_key(groupName):
         petGroups[groupName] = []
      petGroups[groupName].append(pet)
         
   #print(petGroups)

   classes = controllers.species.endangered_classification_map()

   return render_template('dashboard.html', name=current_user.username, petdata=pets, form=petform, searchform=searchform, classifications=classes, groups=petGroups)

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
      if form.cancel.data == True:
         return redirect(url_for('ui.dashboard'))

      if not form.validate_on_submit():
         flash(form.errors, 'danger')
         #print(form.errors)

      if form.submit.data == True:
         status = controllers.pets.pet_note_update(id, note_id, form.data)
      elif form.delete.data == True:
         #print('## we got a note delete for: %s => %s' % (id, note_id))
         status = controllers.pets.pet_note_delete(id, note_id)
      return redirect(url_for('ui.dashboard'))
   elif request.method == 'GET':
      #print('in the get')
      note = controllers.pets.pet_note_get_id(id, note_id)
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
      if form.cancel.data == True:
         return redirect(url_for('ui.dashboard'))

      if not form.validate_on_submit():
         if form.errors['note']:
            flash('Note: ' + form.errors['note'][0], 'danger')
         return render_template('manage_note.html', name=current_user.username, form=form, searchform=searchform, pet_id=id)

      if form.submit.data == True:
         status = controllers.pets.pet_note_create(id, form.data)
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
   #print(request.form)
   #print(request.method)
   #print(json.dumps(form.data))
   if request.method == 'POST':
      if form.cancel.data == True:
         return redirect(url_for('ui.dashboard'))

      #if not form.validate_on_submit():
      #   flash(form.errors, 'danger')
      #   #print(form.errors)

      if form.edit.data == True:
         pet = controllers.pets.pet_lookup_specific(id)
         editForm = forms.PetForm(pet=pet['pet'], species=pet['species'], notes=[])

         return render_template('manage_pet.html', name=current_user.username, petdata=pet, form=editForm, searchform=searchform)
      elif form.submit.data == True:
         pet = controllers.pets.pet_update(id, form.data)
      elif form.delete.data == True:
         status = controllers.pets.pet_delete(id)
      elif form.note.data == True:
         return redirect(url_for('ui.manage_specific_pet_note', id=id))
      return redirect(url_for('ui.dashboard'))
   elif request.method == 'GET':
      pet = controllers.pets.pet_lookup_specific(id)
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
      if form.cancel.data == True:
         return redirect(url_for('ui.dashboard'))

      if not form.validate_on_submit():
         flash(form.errors, 'danger')
         #print(form.errors)
         #print('failed validation')
      #print(form.species.scientific_name.data)

      #print(form.pet)

      q =  controllers.species.species_lookup_scientific(form.species.scientific_name.data)

      if form.submit.data == True:
         pet = controllers.pets.pet_create(form.data)

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


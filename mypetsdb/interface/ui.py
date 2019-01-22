import json

from flask import Flask, request, render_template, redirect, url_for, Blueprint, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from mypetsdb import bootstrap, login_manager
import mypetsdb.controllers.pets 
import mypetsdb.models as models
import mypetsdb.forms as forms

login_manager.login_view = 'ui.login'

@login_manager.user_loader
def load_user(user_id):
   return (models.Session.query(models.User)
            .filter(models.User.id == user_id)
            .first())

routes = Blueprint('ui', __name__, template_folder='templates', static_folder='static')


@routes.route('/')
def index():
   return render_template('index.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
   form = forms.LoginForm()

   if form.validate_on_submit():
      user = (models.Session.query(models.User)
               .filter(models.User.username == form.username.data)
               .first())
      if user:
         if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('ui.dashboard'))

      return '<h1>Invalid username or password</h1>'
      #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

   return render_template('login.html', form=form)

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
   form = forms.RegisterForm()

   if form.validate_on_submit():
      hashed_password = generate_password_hash(form.password.data, method='sha256')
      new_user = models.User(username=form.username.data, email=form.email.data, password=hashed_password)
      models.Session.add(new_user)
      models.Session.commit()

      return '<h1>New user has been created!</h1>'
      #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

   return render_template('signup.html', form=form)

@routes.route('/dashboard')
@login_required
def dashboard():
   form = forms.PetForm()
   p = mypetsdb.controllers.pets.pet_lookup_all()
   return render_template('dashboard.html', name=current_user.username, petdata=p, form=form)

@routes.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('ui.index'))


@routes.route('/pet/manage/<id>', methods = ['GET', 'POST'])
@login_required
def manage_specific_pet(id):
   form = forms.PetForm(request.form)
   print(request.form)
   #print(json.dumps(form.data))
   if request.method == 'POST':
      #print('in post of specific pet')
      # show the edit form 
      if form.edit.data == True:
         pet = mypetsdb.controllers.pets.pet_lookup_specific(id)
         editForm = forms.PetForm(pet=pet['pet'], species=pet['species'], notes=pet['notes'])

         return render_template('manage_pet.html', name=current_user.username, petdata=pet, form=editForm)
      elif form.submit.data == True:
         pet = mypetsdb.controllers.pets.pet_update(id, form.data)

      return redirect(url_for('ui.dashboard'))
   elif request.method == 'GET':
      return render_template('manage_pet.html', name=current_user.username, form=form)



@routes.route('/pet/manage', methods = ['GET', 'POST'])
@login_required
def manage_pet():
   form = forms.PetForm(request.form)
   print(json.dumps(form.data))
   if request.method == 'POST':
      #if form.validate() == False:
      #   print("#### validation failed")
      #   flash('All fields are required.')
      #   return render_template('newpet.html', name=current_user.username, form=form)
      #else:
      #   print("### validation passed")
      pet = mypetsdb.controllers.pets.pet_create(form.data)

      return redirect(url_for('ui.dashboard'))
   elif request.method == 'GET':
      return render_template('manage_pet.html', name=current_user.username, form=form)


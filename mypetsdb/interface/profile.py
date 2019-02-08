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

routes = Blueprint('profile', __name__, template_folder='templates', static_folder='static')


#########################################################
@routes.route('/profile', methods=['GET'])
@login_required
def profile():
   searchform = forms.SearchForm()
   speciesform = forms.PetSpeciesDatumForm()

   user = (models.Session.query(models.User)
           .filter(models.User.username == current_user.username)
           .first())

   return render_template('profile/profile.html', name=current_user.username, form=speciesform, searchform=searchform, user=user)

@routes.route('/profile/email', methods=['POST'])
@login_required
def profile_email():
   searchform = forms.SearchForm()
   speciesform = forms.PetSpeciesDatumForm()

   form = forms.EmailForm(request.form)

   user = (models.Session.query(models.User)
           .filter(models.User.username == current_user.username)
           .first())

   if request.method == 'POST':
      if not form.validate_on_submit():
         flash(form.errors, 'danger')
         return redirect(url_for('profile.profile'))

      if form.submit.data == True:
         print('update that email')
         flash('Information saved', 'success')
   return redirect(url_for('profile.profile'))


@routes.route('/profile/password', methods=['POST'])
@login_required
def profile_password():
   searchform = forms.SearchForm()
   speciesform = forms.PetSpeciesDatumForm()

   form = forms.PasswordForm(request.form)

   user = (models.Session.query(models.User)
           .filter(models.User.username == current_user.username)
           .first())

   if request.method == 'POST':
      #if not form.validate_on_submit():
      #   flash(form.errors, 'danger')
      #   return redirect(url_for('profile.profile'))

      if form.submit.data == True:
         print('update that password')
         flash('Information saved', 'success')
   return redirect(url_for('profile.profile'))



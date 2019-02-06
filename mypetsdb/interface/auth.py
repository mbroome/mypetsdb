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

@login_manager.user_loader
def load_user(user_id):
   return (models.Session.query(models.User)
            .filter(models.User.id == user_id)
            .first())

routes = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


#########################################################
# Auth related endpoints
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

      flash('Invalid username or password', 'warning')

   return render_template('login.html', form=form)

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
   form = forms.RegisterForm()

   if form.validate_on_submit():
      user = (models.Session.query(models.User)
               .filter(models.User.username == form.username.data)
               .first())
      if user:
         #print('### user exists')
         flash('Sorry, ' + form.username.data + ' already exists', 'warning')
         return render_template('signup.html', form=form)

      hashed_password = generate_password_hash(form.password.data, method='sha256')
      new_user = models.User(username=form.username.data, email=form.email.data, password=hashed_password)
      models.Session.add(new_user)
      models.Session.commit()

      flash('User created', 'success')
      return redirect(url_for('auth.login'))

   return render_template('signup.html', form=form)

@routes.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('ui.index'))



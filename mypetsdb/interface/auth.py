import json

from flask import Flask, request, render_template, redirect, url_for, Blueprint, flash, abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

#from sqlalchemy import is_

from mypetsdb import login_manager, ma, ts
import mypetsdb.controllers.auth
#import mypetsdb.controllers.utils

import mypetsdb.models as models
import mypetsdb.forms as forms

from mypetsdb.config import settings
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
         if user.is_correct_password(form.password.data):
            if user.email_confirmed:
               login_user(user, remember=form.remember.data)
               return redirect(url_for('ui.dashboard'))
            else:
               flash('User account not yet verified.  Please check your email', 'warning')
               return render_template('auth/login.html', form=form)

      flash('Invalid username or password', 'warning')

   return render_template('auth/login.html', form=form)

@routes.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('ui.index'))

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
   form = forms.RegisterForm()
   disableEmailVerify = False
   if settings.DISABLE_EMAIL_VERIFY:
      disableEmailVerify = True
   #if 'flask' in config and 'DISABLE_EMAIL_VERIFY' in config['flask'] and config['flask']['DISABLE_EMAIL_VERIFY']:
   #   disableEmailVerify = True

   if form.validate_on_submit():
      user = (models.Session.query(models.User)
               .filter(models.User.username == form.username.data)
               .first())
      if user:
         #print('### user exists')
         flash('Sorry, ' + form.username.data + ' already exists', 'warning')
         return render_template('auth/signup.html', form=form)


      new_user = models.User(username=form.username.data, email=form.email.data, password=form.password.data)
      if disableEmailVerify:
         new_user.email_confirmed = True
         flash('User created', 'success')

      models.Session.add(new_user)
      models.Session.commit()

      if not disableEmailVerify:
         # Now we'll send the email confirmation link
         subject = "Confirm your email"

         token = ts.dumps(form.email.data, salt='email-confirm-key')
         #print(token)
         confirm_url = url_for(
               'auth.confirm_email',
               token=token,
               _external=True)

         html = render_template('email/activate.html', confirm_url=confirm_url)
         #print(html)

         mypetsdb.controllers.auth.send_email([form.email.data], subject=subject, html=html)

         flash('Verification email sent', 'success')
      return redirect(url_for('auth.login'))

   return render_template('auth/signup.html', form=form)

@routes.route('/confirm/<token>')
def confirm_email(token):
   try:
       email = ts.loads(token, salt="email-confirm-key", max_age=86400)
   except:
       abort(404)

   user = (models.Session.query(models.User)
           .filter(models.User.email == email)
           .first())

   if not user:
      flash('Error', 'critical')
      return redirect(url_for('auth.login'))

   user.email_confirmed = True

   models.Session.add(user)
   models.Session.commit()

   flash('User verified.  You can now sign in.', 'success')
   return redirect(url_for('auth.login'))

@routes.route('/reset', methods=["GET", "POST"])
def reset():
    form = forms.EmailForm()
    if form.validate_on_submit():
        user = (models.Session.query(models.User)
                .filter(models.User.email == form.email.data)
                .first())
        if not user:
           return redirect(url_for('auth.login'))

        if not user.email_confirmed:
           flash('User account not yet verified.  Please check your email', 'warning')
           return redirect(url_for('auth.login'))


        subject = "Password reset requested"

        token = ts.dumps(user.email, salt='recover-key')

        recover_url = url_for(
            'auth.reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'auth/recover.html',
            recover_url=recover_url)

        mypetsdb.controllers.auth.send_email([user.email], subject=subject, html=html)

        flash('Password reset email sent', 'success')

        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html', form=form)

@routes.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = forms.PasswordForm()

    if form.validate_on_submit():
        user = (models.Session.query(models.User)
                .filter(models.User.email == email)
                .first())
        if not user:
           abort(404)

        user.password = form.password.data

        models.Session.add(user)
        models.Session.commit()

        flash('Password updated', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_with_token.html', form=form, token=token)


from flask import Flask, render_template, redirect, url_for, Blueprint
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

'''
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class PetSpeciesForm(FlaskForm):
    scientific_name = StringField('scientific_name', validators=[InputRequired(), Length(min=4, max=100)])
    common_name = StringField('common_name', validators=[Length(min=0, max=100)])
    endangered_status = IntegerField('endangered_status')
    iucn_category = StringField('iucn_category', validators=[Length(min=0, max=10)])
    iucn_id = StringField('iucn_id', validators=[Length(min=0, max=20)])
    cares = IntegerField('cares')
    genus = StringField('genus', validators=[Length(min=0, max=40)])
    species = StringField('species', validators=[Length(min=0, max=40)])
'''

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
    p = mypetsdb.controllers.pets.pet_lookup_all()
    form = forms.PetSpeciesForm(obj=p[0].species[0])
    return render_template('dashboard.html', name=current_user.username, petdata=p, form=form)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('ui.index'))

@routes.route('/newpet')
@login_required
def newpet():
    form = forms.PetSpeciesForm()
    return render_template('newpet.html', name=current_user.username, form=form)

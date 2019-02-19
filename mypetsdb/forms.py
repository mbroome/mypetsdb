from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField, FieldList, FormField
from wtforms.validators import InputRequired, DataRequired, Email, Length
from wtforms.fields.html5 import DateField

from datetime import datetime

import mypetsdb.models as models

###################################################
# user management
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])


###################################################
# data management
class SearchForm(FlaskForm):
    petsearch = StringField('Search', validators=[Length(min=4, max=50)], render_kw={"placeholder": "Search My Collection..."})
    speciessearch = StringField('Search', validators=[Length(min=4, max=50)], render_kw={"placeholder": "Species Search..."})

class SpeciesSearchForm(FlaskForm):
    scientific_name = StringField('Scientific Name')
    variety = StringField('Variety')

class NoteDatumForm(FlaskForm):
    note_id =  IntegerField('Note ID')
    public =  BooleanField('Public')
    #note = StringField('Note', validators=[InputRequired(message='A note must be between 4 and 255 characters long'), Length(min=4, max=255)])
    note = StringField('Note', validators=[Length(min=4, max=255)])
    timestamp = DateField('timestamp',format="%m/%d/%Y",default=datetime.now())

    edit = SubmitField('Edit')
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')

class PetSpeciesDatumForm(FlaskForm):
    scientific_name = StringField('Scientific Name')
    variety = StringField('Variety')
    iucn_category = StringField('IUCN Category')
    iucn_id = StringField('IUCN ID')
    cares_category = IntegerField('CARES')
    cares_link = IntegerField('CARES Link')
    planetcatfish_link = IntegerField('PlanetCatfish Link')

class PetDatumForm(FlaskForm):
    pet_id = IntegerField('pet_id')
    variety = StringField('Variety', validators=[Length(min=0, max=50)])
    collection_point = StringField('Collection Point', validators=[Length(min=0, max=50)])
    start = DateField('Start')
    end = DateField('End')
    desc = StringField('Description')
    group_name = StringField('Group')
    public =  BooleanField('Public')

class PetForm(FlaskForm):
    pet = FormField(PetDatumForm)
    species = FormField(PetSpeciesDatumForm)
    notes = FieldList(FormField(NoteDatumForm,min_entries=1))

    edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    submit = SubmitField('Submit')
    note = SubmitField('+Note')
    cancel = SubmitField('Cancel')



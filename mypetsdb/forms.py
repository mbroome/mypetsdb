from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField, FieldList, FormField
from wtforms.validators import InputRequired, Email, Length
from wtforms.fields.html5 import DateField

from datetime import datetime

import mypetsdb.models as models

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class SearchForm(FlaskForm):
    petsearch = StringField('Search', [InputRequired()], render_kw={"placeholder": "Pet Search..."})
    speciessearch = StringField('Search', [InputRequired()], render_kw={"placeholder": "Species Search..."})

#class SpeciesSearchForm(FlaskForm):

class NoteDatumForm(FlaskForm):
    note_id =  IntegerField('Note ID')
    public =  BooleanField('Public')
    note = StringField('Note')
    timestamp = DateField('timestamp',format="%m/%d/%Y",default=datetime.now())

    edit = SubmitField('Edit')
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')

class SpeciesDatumForm(FlaskForm):
    scientific_name = StringField('Scientific Name')
    common_name = StringField('Common Name')
    endangered_status = IntegerField('Endangered Status')
    iucn_category = StringField('IUCN Category')
    iucn_id = StringField('IUCN ID')
    cares = IntegerField('CARES')

class PetDatumForm(FlaskForm):
    pet_id = IntegerField('pet_id')
    variant = StringField('Variant')
    collection_point = StringField('Collection Point')
    start = DateField('Start')
    end = DateField('End')
    desc = StringField('Description')
    public =  BooleanField('Public')

class PetForm(FlaskForm):
    pet = FormField(PetDatumForm)
    species = FormField(SpeciesDatumForm)
    notes = FieldList(FormField(NoteDatumForm,min_entries=1))

    edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    submit = SubmitField('Submit')
    note = SubmitField('+Note')
    cancel = SubmitField('Cancel')


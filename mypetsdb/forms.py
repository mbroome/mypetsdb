from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, SubmitField, FieldList, FormField
from wtforms.validators import InputRequired, Email, Length

import mypetsdb.models as models

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class NoteForm(FlaskForm):
    note_id =  IntegerField('note_id')
    public =  BooleanField('public')
    note = StringField('note', validators=[Length(min=4, max=255)])
    timestamp = DateField('timestamp')
    submit = SubmitField('Submit')

class PetSpeciesForm(FlaskForm):
    scientific_name = StringField('Scientific Name')
    common_name = StringField('Common Name')
    endangered_status = IntegerField('Endangered Status')
    iucn_category = StringField('IUCN Category')
    iucn_id = StringField('IUCN ID')
    cares = IntegerField('CARES')

class PetForm(FlaskForm):
    pet_id = IntegerField('pet_id')
    variant = StringField('Variant')
    collection_point = StringField('Collection Point')
    start = DateField('Start')
    end = DateField('End')
    description =  StringField('Description')
    public =  BooleanField('Public')

    species = FieldList(FormField(PetSpeciesForm),min_entries=1)

    edit = SubmitField('Edit')
    submit = SubmitField('Submit')
    note = SubmitField('Notes')


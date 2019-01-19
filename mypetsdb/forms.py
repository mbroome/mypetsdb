from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, SubmitField
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

class PetForm(FlaskForm):
    #pet_id = IntegerField('pet_id')
    variant = StringField('variant')
    collection_point = StringField('collection_point')
    start = DateField('start')
    end = DateField('end')
    description =  StringField('description')
    public =  BooleanField('public')
    scientific_name = StringField('scientific_name')
    submit = SubmitField('Add')

class NoteForm(FlaskForm):
    note_id =  IntegerField('note_id')
    public =  BooleanField('public')
    note = StringField('note', validators=[Length(min=4, max=255)])
    timestamp = DateField('timestamp')
    submit = SubmitField('Submit')

class PetSpeciesForm(FlaskForm):
    scientific_name = StringField('scientific_name', validators=[InputRequired(), Length(min=4, max=100)])
    common_name = StringField('common_name', validators=[Length(min=0, max=100)])
    endangered_status = IntegerField('endangered_status')
    iucn_category = StringField('iucn_category', validators=[Length(min=0, max=10)])
    iucn_id = StringField('iucn_id', validators=[Length(min=0, max=20)])
    cares = IntegerField('cares')
    genus = StringField('genus', validators=[Length(min=0, max=40)])
    species = StringField('species', validators=[Length(min=0, max=40)])




from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
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

class PetSpeciesForm(FlaskForm):
    scientific_name = StringField('scientific_name', validators=[InputRequired(), Length(min=4, max=100)])
    common_name = StringField('common_name', validators=[Length(min=0, max=100)])
    endangered_status = IntegerField('endangered_status')
    iucn_category = StringField('iucn_category', validators=[Length(min=0, max=10)])
    iucn_id = StringField('iucn_id', validators=[Length(min=0, max=20)])
    cares = IntegerField('cares')
    genus = StringField('genus', validators=[Length(min=0, max=40)])
    species = StringField('species', validators=[Length(min=0, max=40)])




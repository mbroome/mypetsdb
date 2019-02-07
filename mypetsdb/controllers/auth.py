from flask import Flask, request, jsonify, render_template
import os
import json
import requests
import time
import datetime

import boto3
from flask_login import current_user
from sqlalchemy import func, or_
from itsdangerous import URLSafeTimedSerializer

import mypetsdb.controllers.utils

config = mypetsdb.controllers.utils.loadConfig()

def send_email(recipients, subject='', text='', html=''):
   ses = None
   if 'aws' in config:
      ses = boto3.client(
         'ses',
         region_name=config['aws']['region'],
         aws_access_key_id=config['aws']['access'],
         aws_secret_access_key=config['aws']['secret']
      )
   else:
      ses = boto3.client('ses')

   sender = config['flask']['SES_EMAIL_FROM']

   ses.send_email(
      Source=sender,
      Destination={'ToAddresses': recipients},
      Message={
         'Subject': {'Data': subject},
         'Body': {
            'Text': {'Data': text},
            'Html': {'Data': html}
         }
      }
   )


def emailTest():
   recipients = ['mitchell.broome@gmail.com']
   subject = 'Thanks for registering'

   # You can render the message using Jinja2
   html = render_template('email/test.html', name='John Doe')

   send_email(recipients=recipients,
              subject=subject,
              html=html
              )
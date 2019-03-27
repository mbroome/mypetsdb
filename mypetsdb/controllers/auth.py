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

from config import settings


def send_email(recipients, subject='', text='', html=''):
   ses = None
   if settings.AWS_ACCESS_KEY_ID:
      ses = boto3.client(
         'ses',
         region_name=settings.AWS_DEFAULT_REGION,
         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
      )
   else:
      ses = boto3.client('ses', region_name='us-east-1')

   sender = settings.SES_EMAIL_FROM

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


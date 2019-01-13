from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
import os
import json

app = Flask(__name__)
#basedir = os.path.abspath(os.path.dirname(__file__))
ma = Marshmallow(app)


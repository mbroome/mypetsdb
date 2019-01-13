from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
import os
import json

from sqlalchemy import Column, Integer, Unicode, Table
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('mysql://aquadb:wzUIrLafJ5nR@localhost/aquadb?charset=latin1', echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
mysession = scoped_session(Session)

ma = Marshmallow(app)

Base = declarative_base()
Base.metadata.bind = engine

class ITISCommonName(Base):
    __table__ = Table('itis_common_names', Base.metadata,
                      Column('tsn', Integer, primary_key=True),
                      autoload=True,
                      autoload_with=engine)

class ITISSpecies(Base):
    __table__ = Table('itis_species', Base.metadata,
                      Column('tsn', Integer, primary_key=True),
                      autoload=True,
                      autoload_with=engine)

Base.metadata.reflect(bind=engine)

class ITISCommonNameSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('tsn', 'vernacular_name','unit_name1','unit_name2','complete_name')
itiscommonname_schema = ITISCommonNameSchema()
itiscommonnames_schema = ITISCommonNameSchema(many=True)

class ITISSpeciesSchema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ('tsn', 'unit_name1','unit_name2','complete_name')
itisspecies_schema = ITISSpeciesSchema()
itisspeciess_schema = ITISSpeciesSchema(many=True)

# endpoint to get user detail by id
@app.route("/species/<id>", methods=["GET"])
def species_lookup(id):
   q = (mysession.query(ITISCommonName)
       .filter(ITISCommonName.vernacular_name.ilike('%{0}%'.format(id)))
       .all())

   if q:
      return(itiscommonnames_schema.jsonify(q))
   else:
      q = (mysession.query(ITISSpecies)
          .filter(ITISSpecies.complete_name.ilike('%{0}%'.format(id)))
          .all())
      return(itisspeciess_schema.jsonify(q))
   


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

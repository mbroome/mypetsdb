import os
import json

from sqlalchemy import Column, Date, DateTime, Index, Integer, String, Text, Table, Boolean, ARRAY
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.dialects.mysql import TIMESTAMP

from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlalchemy.exc
from sqlalchemy.sql import select, text

from flask_login import UserMixin

try:
   contents = open('/etc/config/mypetsdb.json', 'r').read()
   config = json.loads(contents)
except:
   config = {'db':{
                  'mypetsdb': 'mysql://mypetsdb:wzUIrLafJ5nR@localhost/mypetsdb?charset=utf8',
                  'itis': 'mysql://mypetsdb:wzUIrLafJ5nR@localhost/ITIS?charset=latin1'
                 }
            }


basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine(config['db']['mypetsdb'], pool_pre_ping=True)
sess = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(sess)

Base = declarative_base()
Base.metadata.bind = engine

class PetDatum(Base):
    __tablename__ = 'pet_data'

    pet_id = Column(Integer, primary_key=True)
    variant = Column(String(100))
    collection_point = Column(String(100))
    userid = Column(String(100), nullable=False)
    start = Column(Date)
    end = Column(Date)
    desc = Column(String(255))
    public = Column(Boolean, nullable=False, default=False)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

    scientific_name = Column(String(100))

class PetNoteDatum(Base):
    __tablename__ = 'pet_note'

    note_id = Column(Integer, primary_key=True, autoincrement=True)
    public = Column(Boolean, nullable=False, default=False)
    note = Column(Text)
    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False, server_default=FetchedValue())

    pet_id = Column(Integer, nullable=False)

class PetSpeciesDatum(Base):
    __tablename__ = 'species_data'

    scientific_name = Column(String(100), primary_key=True)
    endangered_status = Column(Integer, nullable=True)
    iucn_category = Column(String(10), nullable=True)
    iucn_id = Column(String(20), nullable=True)
    cares = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())


class CommonNameXREF(Base):
    __tablename__ = 'common_names_xref'

    common_name = Column(String(100), primary_key=True, nullable=False)
    scientific_name = Column(String(100), primary_key=True, nullable=False)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

    xref_id = Column(Integer, nullable=True)

class SpeciesNameXREF(Base):
    __tablename__ = 'species_names_xref'

    scientific_name = Column(String(100), primary_key=True, nullable=False)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False, server_default=FetchedValue())

    xref_id = Column(Integer, nullable=True)

class EndangeredClasificationXREF(Base):
    __tablename__ = 'endangered_clasification_xref'

    code = Column(String(10), primary_key=True, nullable=False)
    name  = Column(String(30), nullable=True)
    description  = Column(String(512), nullable=True)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

class CaresXREF(Base):
    __tablename__ = 'cares_xref'

    scientific_name = Column(String(100), primary_key=True, nullable=False)
    code = Column(String(10), primary_key=True, nullable=False)
    assessment  = Column(String(50), nullable=True)
    authority  = Column(String(50), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(80))


def loadITISData():
   itis_engine = create_engine(config['db']['itis'], pool_pre_ping=True)

   '''
   species_query = text('select unit_name1,unit_name2,tsn from taxonomic_units where unit_name1!="" and unit_name2!=""')
   species_list = itis_engine.execute(species_query).fetchall()
   print(len(species_list))
   print(species_list[0])

   for species in species_list:
      scientific_name = "%s %s" % (species[0], species[1])

      rec = {'scientific_name': scientific_name.lower(),
             'xref_id': species[2],
             'source': 'itis'}
      print(rec)
      try:
         engine.execute(SpeciesNameXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass
   '''

   common_query = text('select v.tsn, v.vernacular_name, t.unit_name1, t.unit_name2, t.complete_name from vernaculars v, taxonomic_units t where v.tsn=t.tsn and t.unit_name2 != "" and language = "english"')
   common_list = itis_engine.execute(common_query).fetchall()
   print(len(common_list))
   print(common_list[0])

   for common in common_list:
      scientific_name = "%s %s" % (common[2], common[3])

      rec = {'scientific_name': scientific_name.lower(),
             'common_name': common[1],
             'xref_id': common[0],
             'source': 'itis'}
      print(rec)
      try:
         engine.execute(CommonNameXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

def loadCARESData():
   dataFile = '../data/cares-1-29-2019.json'
   contents = open(dataFile, 'r').read()
   data = json.loads(contents)

   #print(data)
   #EndangeredClasificationXREF
   for classification in data['classifications']:
      rec = {'code': classification['key'],
             'name': classification['classification'],
             'description': classification['description'],
             'source': 'cares'}
      print(rec)
      print(len(rec['description']))
      try:
         engine.execute(EndangeredClasificationXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

   for species in data['species']:
      rec = {'scientific_name': species['species'].lower(),
             'code': species['classification'][:species['classification'].find(' ')],
             'assessment': species['assessment'],
             'authority': species['authority']}
      print(rec)
      try:
         engine.execute(CaresXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass


Base.metadata.reflect(bind=engine)

if __name__ == '__main__':
   Base.metadata.create_all()

   #loadITISData()
   loadCARESData()


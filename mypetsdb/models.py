import os
import glob
import json

from sqlalchemy import Column, Date, DateTime, Index, Integer, String, Text, Table, Boolean, ARRAY, UniqueConstraint
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.sql import expression

from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlalchemy.exc
from sqlalchemy.sql import select, text
from sqlalchemy.ext.hybrid import hybrid_property

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

try:
   from mypetsdb.controllers.utils import loadConfig
except:
   from controllers.utils import loadConfig

config = loadConfig()

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine(config['db']['mypetsdb'], pool_pre_ping=True)
sess = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(sess)

Base = declarative_base()
Base.metadata.bind = engine

###############################################
# pet related data points
class PetDatum(Base):
    __tablename__ = 'pet_data'

    pet_id = Column(Integer, primary_key=True, autoincrement=True)
    variety = Column(String(50))
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

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name = Column(String(100), unique=True)
    iucn_category = Column(String(10), nullable=False, server_default='')
    iucn_id = Column(String(20), nullable=False, server_default='')
    cares_category = Column(String(10), nullable=False, server_default='')
    cares_link = Column(String(255), nullable=False, server_default='')
    planetcatfish_link = Column(String(255), nullable=False, server_default='')
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

class SpeciesVarietyDatum(Base):
    __tablename__ = 'species_variety_data'

    variety_id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name = Column(String(100), nullable=False)
    variety = Column(String(50), nullable=False)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False, server_default=FetchedValue())

    __table_args__ = (
       UniqueConstraint('scientific_name', 'variety', name='u_sn_v'),
    )

###############################################
# xref tables
class CommonNameXREF(Base):
    __tablename__ = 'common_names_xref'

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    common_name = Column(String(100), nullable=False)
    scientific_name = Column(String(100), nullable=False)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())
    xref_id = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint('scientific_name', 'common_name', name='u_cname_xref'),
    )


class SpeciesNameXREF(Base):
    __tablename__ = 'species_names_xref'

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name = Column(String(100), primary_key=True, nullable=False, unique=True)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())
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

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False)
    assessment  = Column(String(50), nullable=True)
    authority  = Column(String(50), nullable=True)
    link = Column(String(255), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

class PlanetCatfishXREF(Base):
    __tablename__ = 'planetcatfish_xref'

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name = Column(String(100), nullable=False)
    common_name = Column(String(100), nullable=False)
    link = Column(String(255), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

class SeriouslyFishXREF(Base):
    __tablename__ = 'seriouslyfish_xref'

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name = Column(String(100), nullable=False)
    link = Column(String(255), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

###############################################
# auth tables
class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    email = Column(String(50), unique=True)
    _password = Column(String(128))
    email_confirmed = Column(Boolean, nullable=False, default=False, server_default=expression.false())

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = generate_password_hash(plaintext, method='sha256')

    def is_correct_password(self, plaintext):
        return check_password_hash(self._password, plaintext)

def loadITISData():
   itis_engine = create_engine(config['db']['itis'], pool_pre_ping=True)

   
   species_query = text('select complete_name,tsn from taxonomic_units where unit_name1!="" and unit_name2!=""')
   species_list = itis_engine.execute(species_query).fetchall()
   print(len(species_list))
   print(species_list[0])

   for species in species_list:
      rec = {'scientific_name': species[0].lower(),
             'xref_id': species[1],
             'source': 'itis'}
      print(rec)
      try:
         engine.execute(SpeciesNameXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

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

   for classification in data['classifications']:
      rec = {'code': classification['key'],
             'name': classification['classification'],
             'description': classification['description'],
             'source': 'cares'}
      #print(rec)
      try:
         engine.execute(EndangeredClasificationXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

   for species in data['species']:
      rec = {'scientific_name': species['species'].lower(),
             'code': species['classification'][:species['classification'].find(' ')],
             'assessment': species['assessment'],
             'link': species['link'],
             'authority': species['authority']}
      #print(rec)
      try:
         engine.execute(CaresXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

      rec = {'scientific_name': species['species'].lower(),
             'source': 'cares'}

      try:
         engine.execute(SpeciesNameXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass


def loadPlanetCatfishData():
   dataFile = '../data/planetcatfish-2-4-2019.json'
   contents = open(dataFile, 'r').read()
   data = json.loads(contents)

   for row in data:
      rec = {'scientific_name': row['scientific_name'].lower(),
             'source': 'planetcatfish'}

      try:
         engine.execute(SpeciesNameXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

      rec = {'scientific_name': row['scientific_name'].lower(),
             'common_name': row['common_name'].lower(),
             'source': 'planetcatfish'}
      print(rec)
      try:
         engine.execute(CommonNameXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

      rec = {'scientific_name': row['scientific_name'].lower(),
             'common_name': row['common_name'].lower(),
             'link': row['link']}
      print(rec)
      try:
         engine.execute(PlanetCatfishXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass


def loadSeriouslyFishData():
   dataFile = '../data/seriouslyfish-2-7-2019.json'
   contents = open(dataFile, 'r').read()
   data = json.loads(contents)

   for row in data:
      rec = {'scientific_name': row['scientific_name'].lower(),
             'source': 'seriouslyfish'}
      try:
         engine.execute(SpeciesNameXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass

      rec = {'scientific_name': row['scientific_name'].lower(),
             'link': row['link']}
      print(rec)
      try:
         engine.execute(SeriouslyFishXREF.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass


def loadVarietyData():
   dataDir = '../data/variety'

   for dataFile in glob.glob(dataDir + '/*.json'):
      contents = open(dataFile, 'r').read()
      data = json.loads(contents)

      for row in data:
         rec = {'scientific_name': row['scientific_name'].lower(),
                'source': row['source']}
         try:
            engine.execute(SpeciesNameXREF.__table__.insert().values(rec))
         except sqlalchemy.exc.IntegrityError:
            pass

         rec = {'scientific_name': row['scientific_name'].lower(),
                'variety': row['variety'].lower(),
                'source': row['source']}
         print(rec)
         try:
            engine.execute(SpeciesVarietyDatum.__table__.insert().values(rec))
         except sqlalchemy.exc.IntegrityError:
            pass

Base.metadata.reflect(bind=engine)

if __name__ == '__main__':
   Base.metadata.create_all()

   #loadITISData()
   #loadCARESData()
   #loadPlanetCatfishData()
   #loadSeriouslyFishData()
   loadVarietyData()


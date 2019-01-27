import os
import json

from sqlalchemy import Column, Date, DateTime, Index, Integer, String, Text, Table, Boolean
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
                  'mypetsdb': 'mysql://mypetsdb:wzUIrLafJ5nR@localhost/mypetsdb?charset=latin1',
                  'itis': 'mysql://mypetsdb:wzUIrLafJ5nR@localhost/ITIS?charset=latin1'
                 }
            }


basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine(config['db']['mypetsdb'], pool_pre_ping=True)
sess = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(sess)

Base = declarative_base()
Base.metadata.bind = engine

#class ITISCommonName(Base):
#    __table__ = Table('itis_common_names', Base.metadata,
#                      Column('tsn', Integer, primary_key=True),
#                      Column('vernacular_name', String(80), primary_key=True),
#                      autoload=True,
#                      autoload_with=engine)
#
#class ITISSpecies(Base):
#    __table__ = Table('itis_species', Base.metadata,
#                      Column('tsn', Integer, primary_key=True),
#                      autoload=True,
#                      autoload_with=engine)
#
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

class SpeciesDatum(Base):
    __tablename__ = 'species_data'

    scientific_name = Column(String(100), primary_key=True)
    common_name = Column(String(100), nullable=True)
    endangered_status = Column(Integer, nullable=True)
    iucn_category = Column(String(10), nullable=True)
    iucn_id = Column(String(20), nullable=True)
    cares = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())


class CommonNameDatum(Base):
    __tablename__ = 'common_names'

    common_name = Column(String(100), primary_key=True, nullable=False)
    scientific_name = Column(String(100), primary_key=True, nullable=False)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

    xref_id = Column(Integer, nullable=True)

class SpeciesNameDatum(Base):
    __tablename__ = 'species_names'

    scientific_name = Column(String(100), primary_key=True, nullable=False)
    source = Column(String(20), nullable=True)
    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False, server_default=FetchedValue())

    xref_id = Column(Integer, nullable=True)

class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(80))


def loadSpeciesData():
   itis_engine = create_engine(config['db']['itis'], pool_pre_ping=True)
   #itis_sess = sessionmaker(autocommit=False, autoflush=False, bind=itis_engine)
   #itis_session = scoped_session(itis_sess)

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
         engine.execute(SpeciesNameDatum.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass


Base.metadata.reflect(bind=engine)

if __name__ == '__main__':
   Base.metadata.create_all()

   loadSpeciesData()

   '''
   common_names = (Session.query(ITISCommonName)
      .filter(ITISCommonName.language.like('%english%'))
      .all())

   for name in common_names:
      #print(name)
      common_name = name.vernacular_name.lower()
      #common_name = common_name.encode('ascii', 'ignore').decode('ascii')

      scientific_name = name.complete_name.lower()
      #scientific_name = scientific_name.encode('ascii', 'ignore').decode('ascii')
      if ' ssp. ' in scientific_name:
         scientific_name = scientific_name[:scientific_name.find(' ssp. ')]
      if ' var. ' in scientific_name:
         scientific_name = scientific_name[:scientific_name.find(' var. ')]

      rec = {'common_name': common_name,
             'scientific_name': scientific_name,
             'xref_id': name.tsn,
             'source': 'itis'}
      if 'apisto' in scientific_name:
         print(rec)

      try:
         engine.execute(CommonNameDatum.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass
   

   species_names = (Session.query(ITISSpecies).all())

   for name in species_names:
      #print(name)
      scientific_name = name.complete_name.lower()
      #scientific_name = scientific_name.encode('ascii', 'ignore').decode('ascii')
      if ' ssp. ' in scientific_name:
         scientific_name = scientific_name[:scientific_name.find(' ssp. ')]
      if ' var. ' in scientific_name:
         scientific_name = scientific_name[:scientific_name.find(' var. ')]

      rec = {'scientific_name': scientific_name,
             'xref_id': name.tsn,
             'source': 'itis'}
      print(rec)
      try:
         engine.execute(SpeciesNameDatum.__table__.insert().values(rec))
      except sqlalchemy.exc.IntegrityError:
         pass
   ''' 

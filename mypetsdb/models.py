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

from flask_login import UserMixin

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('mysql://mypetsdb:wzUIrLafJ5nR@localhost/mypetsdb?charset=latin1', pool_pre_ping=True)
#engine = create_engine('mysql://mypetsdb:wzUIrLafJ5nR@localhost/mypetsdb?charset=latin1', pool_pre_ping=True, echo=True)
sess = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(sess)

Base = declarative_base()
Base.metadata.bind = engine

class ITISCommonName(Base):
    __table__ = Table('itis_common_names', Base.metadata,
                      Column('tsn', Integer, primary_key=True),
                      Column('vernacular_name', String(80), primary_key=True),
                      autoload=True,
                      autoload_with=engine)

class ITISSpecies(Base):
    __table__ = Table('itis_species', Base.metadata,
                      Column('tsn', Integer, primary_key=True),
                      autoload=True,
                      autoload_with=engine)

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


Base.metadata.reflect(bind=engine)

if __name__ == '__main__':
   Base.metadata.create_all()

   
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
  

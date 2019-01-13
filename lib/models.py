import os
import json

from sqlalchemy import Column, Integer, Unicode, Table
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import scoped_session, sessionmaker

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('mysql://aquadb:wzUIrLafJ5nR@localhost/aquadb?charset=latin1', echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
mysession = scoped_session(Session)

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

class PetData(Base):
    __table__ = Table('pet_data', Base.metadata,
                      autoload=True,
                      autoload_with=engine)

class PetNote(Base):
    __table__ = Table('pet_note', Base.metadata,
                      autoload=True,
                      autoload_with=engine)

class SpeciesData(Base):
    __table__ = Table('species_data', Base.metadata,
                      autoload=True,
                      autoload_with=engine)


Base.metadata.reflect(bind=engine)


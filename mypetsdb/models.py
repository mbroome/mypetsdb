import os
import json

from sqlalchemy import Column, DateTime, Index, Integer, String, Text, Table, Boolean
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.dialects.mysql import TIMESTAMP

from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_login import UserMixin

basedir = os.path.abspath(os.path.dirname(__file__))
#engine = create_engine('mysql://aquadb:wzUIrLafJ5nR@localhost/aquadb?charset=latin1', echo=True)
engine = create_engine('mysql://aquadb:wzUIrLafJ5nR@localhost/aquadb?charset=latin1')
sess = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(sess)

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

pet_species = Table('pet_species',
   Base.metadata,
   Column('pet_id', Integer, ForeignKey('pet_data.pet_id')),
   Column('scientific_name', String(100), ForeignKey('species_data.scientific_name'))
)

class PetDatum(Base):
    __tablename__ = 'pet_data'

    pet_id = Column(Integer, primary_key=True)
    variant = Column(String(100))
    collection_point = Column(String(100))
    userid = Column(String(100), nullable=False)
    start = Column(DateTime)
    end = Column(DateTime)
    description = Column(String(255))
    public = Column(Boolean, nullable=False, server_default=FetchedValue())

    species = relationship('SpeciesDatum',secondary=pet_species, backref=backref('pet', lazy='joined'))
    notes = relationship('PetNote', backref='pet', lazy='joined')

class PetNote(Base):
    __tablename__ = 'pet_note'

    note_id = Column(Integer, primary_key=True, autoincrement=True)
    public = Column(Boolean, nullable=False, server_default=FetchedValue())
    note = Column(Text)
    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False, server_default=FetchedValue())

    pet_id = Column(Integer, ForeignKey('pet_data.pet_id'))

class SpeciesDatum(Base):
    __tablename__ = 'species_data'

    scientific_name = Column(String(100), primary_key=True)
    common_name = Column(String(100), nullable=True)
    endangered_status = Column(Integer, nullable=False, server_default=FetchedValue())
    iucn_category = Column(ENUM(u'DD', u'LC', u'NT', u'VU', u'EN', u'CR', u'EW', u'EX', u'LR/lc', u'LR/nt', u'LR/cd'))
    iucn_id = Column(String(20))
    cares = Column(Integer, nullable=False, server_default=FetchedValue())
    genus = Column(String(40), nullable=False)
    species = Column(String(40), nullable=False)


class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(80))


Base.metadata.reflect(bind=engine)

if __name__ == '__main__':
   Base.metadata.create_all()



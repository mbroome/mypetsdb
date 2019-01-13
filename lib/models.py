import os
import json

from sqlalchemy import Column, DateTime, Index, Integer, String, Text, Table
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.mysql.enumerated import ENUM

from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import scoped_session, sessionmaker

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('mysql://aquadb:wzUIrLafJ5nR@localhost/aquadb?charset=latin1', echo=True)
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

class PetDatum(Base):
    __tablename__ = 'pet_data'
    #__table_args__ = (
    #    Index('scientific_name', 'scientific_name', 'variant', 'userid'),
    #    {u'schema': 'aquadb'}
    #)

    pet_id = Column(Integer, primary_key=True)
    #scientific_name = Column(String(100), nullable=False)
    variant = Column(String(100))
    collection_point = Column(String(100))
    userid = Column(String(100), nullable=False)
    start = Column(DateTime)
    end = Column(DateTime)
    description = Column(String(255))
    public = Column(Integer, nullable=False, server_default=FetchedValue())

    notes = relationship('PetNote')
    scientific_name = Column(String(100), ForeignKey('species_data.scientific_name'))


class PetNote(Base):
    __tablename__ = 'pet_note'
    #__table_args__ = {u'schema': 'aquadb'}

    note_id = Column(Integer, primary_key=True, nullable=False)
    pet_id = Column(Integer, ForeignKey('pet_data.pet_id'))
    public = Column(Integer, nullable=False, server_default=FetchedValue())
    note = Column(Text)
    timestamp = Column(DateTime, primary_key=True, nullable=False, server_default=FetchedValue())


class SpeciesDatum(Base):
    __tablename__ = 'species_data'
    #__table_args__ = {u'schema': 'aquadb'}

    scientific_name = Column(String(100), primary_key=True)
    common_name = Column(String(100), nullable=True)
    endangered_status = Column(Integer, nullable=False, server_default=FetchedValue())
    iucn_category = Column(ENUM(u'DD', u'LC', u'NT', u'VU', u'EN', u'CR', u'EW', u'EX', u'LR/lc', u'LR/nt', u'LR/cd'))
    iucn_id = Column(String(20))
    cares = Column(Integer, nullable=False, server_default=FetchedValue())
    genus = Column(String(40), nullable=False)
    species = Column(String(40), nullable=False)

    pet = relationship('PetDatum')


Base.metadata.reflect(bind=engine)

if __name__ == '__main__':
   Base.metadata.create_all()


from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema

from geoalchemy2 import Geometry

from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import Base

# TODO: Before use pgterm later maybe with sqlalchemy utils
#       CREATE DATABASE IF NOT EXISTS postgres_alchemy;
#       \c postgres_alchemy;
#       CREATE EXTENSION IF NOT EXISTS "postgis";
#       CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres_alchemy', echo=True)
if not engine.dialect.has_schema(engine, 'public'):
    engine.execute(CreateSchema('public'))
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

# Base = declarative_base()

# class Lake(Base):
#   __tablename__ = 'lake'
#   id = Column(Integer, primary_key=True)
#   name = Column(String)
#   name2 = Column(String)
#   geom = Column(Geometry('POLYGON'))


# Base.metadata.create_all(engine)


# lake = Lake(name='Majeur', name2="asdf", geom='POLYGON((0 0,1 0,1 1,0 1,0 0))')
# session = Session()
# session.add(lake)
# session.commit()
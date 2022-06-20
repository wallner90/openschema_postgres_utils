from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry

from sqlalchemy.orm import sessionmaker


engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Lake(Base):
  __tablename__ = 'lake'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  name2 = Column(String)
  geom = Column(Geometry('POLYGON'))


Base.metadata.create_all(engine)


lake = Lake(name='Majeur', name2="asdf", geom='POLYGON((0 0,1 0,1 1,0 1,0 0))')
session = Session()
session.add(lake)
session.commit()
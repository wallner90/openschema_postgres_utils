from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema

from geoalchemy2 import Geometry

from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import *

# TODO: Before use pgterm later maybe with sqlalchemy utils
#       CREATE DATABASE IF NOT EXISTS postgres_alchemy;
#       \c postgres_alchemy;
#       CREATE EXTENSION IF NOT EXISTS "postgis";
#       CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# TODO check lazy.
engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy', echo=True)
if not engine.dialect.has_schema(engine, 'public'):
    engine.execute(CreateSchema('public'))
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

posegraph = PoseGraph(description='Test graph')

imu = IMU(topic='/imu', description='An imu')
posegraph.sensors = [imu]

# or the other way round

vertices = [
    Vertex(position=f'POINTZ(0 0 {i})', posegraph=posegraph) for i in range(3)]

edges = [Edge(from_vertex=vertices[0], to_vertex=vertices[1]),
         Edge(from_vertex=vertices[1], to_vertex=vertices[0]),
         Edge(from_vertex=vertices[0], to_vertex=vertices[2]),
         Edge(from_vertex=vertices[2], to_vertex=vertices[1])]

session = Session()
session.add_all([posegraph, imu, *vertices, *edges])
session.commit()


print(f'{vertex}' for vertex in vertices)

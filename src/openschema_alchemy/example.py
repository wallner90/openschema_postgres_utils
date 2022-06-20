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
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres_alchemy', echo=True)
if not engine.dialect.has_schema(engine, 'public'):
    engine.execute(CreateSchema('public'))
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


posegraph = PoseGraph(description='Test graph')

imu = IMU(topic='/imu', description='An imu')
posegraph.sensors = [imu]

# or the other way round

vertex = [ Vertex(position=f'POINTZ(0 0 {i})', posegraph=posegraph)  for i in range(3)]

edge = Edge(from_vertex=vertex[0], to_vertex=vertex[1])
edge2 = Edge(from_vertex=vertex[1], to_vertex=vertex[0])
edge3 = Edge(from_vertex=vertex[0], to_vertex=vertex[2])
edge4 = Edge(from_vertex=vertex[2], to_vertex=vertex[1])


session = Session()

session.add_all([posegraph, imu, *vertex, edge, edge2, edge3, edge4])
session.commit()

print(vertex)

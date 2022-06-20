from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema

from geoalchemy2 import Geometry, func

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

num_vertices = 500

vertices = [
    Vertex(position=f'POINTZ({2*i} {3*i} {i})', posegraph=posegraph) for i in range(num_vertices)]

edges = [Edge(from_vertex=vertices[i],
              to_vertex=vertices[(i+1) % num_vertices]) for i in range(num_vertices)]

session = Session()
session.add_all([posegraph, imu, *vertices, *edges])
session.commit()


for edge in edges:
    dist = session.query(func.ST_Distance(
        edge.from_vertex.position, edge.to_vertex.position)).one()
    print(f"Edge {edge} has length {dist}m.")

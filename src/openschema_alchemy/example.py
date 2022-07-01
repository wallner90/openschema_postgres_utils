from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema

from geoalchemy2 import Geometry, func

from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import *
from datetime import datetime, timedelta

# TODO: Before use pgterm later maybe with sqlalchemy utils
#       CREATE DATABASE IF NOT EXISTS postgres_alchemy_ait;
#       \c postgres_alchemy_ait;
#       CREATE SCHEMA IF NOT EXISTS "public";
#       CREATE EXTENSION IF NOT EXISTS "postgis";
#       CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# TODO check lazy.

# TODO: Time in TAI might be better??
engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', echo=True,
     connect_args={"options": "-c timezone=utc"})
if not engine.dialect.has_schema(engine, 'public'):
    engine.execute(CreateSchema('public'))
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

sensor_rig = SensorRig(name='A vehicle sensor rig', description={'T': [0.0]*12})
camera = Camera(name='A camera', description={'P': [0.0]*16}, sensor_rig=sensor_rig)

ts = datetime.utcnow()
newmap = Map(name='A test map', description={'T_global': [0.0]*12}, created_at=ts, updated_at=ts)

pg = PoseGraph(name='SLAM graph', description={'Some_generic_setting': 0.2})
sensor_rig.posegraph = pg
num_vertices = 500

pg.map = newmap

poses = [Pose(position=f'POINTZ({2*i} {3*i} {i})', posegraph=pg) for i in range(num_vertices)]
for i in poses[1:]:
    i.parent = poses[0]

time_delta = timedelta(milliseconds=33)
observations = [CameraObservation(
                created_at=ts + time_delta*i,
                updated_at=ts + time_delta*i, pose=p,
                sensor=camera,
                camera=camera)
              for i, p in enumerate(poses)
              ]
# TODO: Landmarks
# TODO: Semantic info

session = Session()
session.add_all([newmap, pg, sensor_rig, camera] + poses + observations)
session.commit()

session.commit()

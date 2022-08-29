from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema

from geoalchemy2 import Geometry, func

from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import *
from datetime import datetime, timedelta

from openschema_alchemy.vi_map import VImap

# TODO: Before use pgterm later maybe with sqlalchemy utils
#       CREATE DATABASE IF NOT EXISTS postgres_alchemy_ait;
#       \c postgres_alchemy_ait;
#       CREATE SCHEMA IF NOT EXISTS "public";
#       CREATE EXTENSION IF NOT EXISTS "postgis";
#       CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# TODO check lazy.

ts = datetime.utcnow()

# load vi-map
vimap = VImap('/data/iviso/_OpenSCHEMA/Knapp_Dobl/dobl_halle_tagged/aaadfd42874eeb161400000000000000')

# TODO: Time in TAI might be better??
engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', echo=True,
     connect_args={"options": "-c timezone=utc"})
if not engine.dialect.has_schema(engine, 'public'):
    engine.execute(CreateSchema('public'))
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

# TODO: get this information from config, along with calib!
sensor_rig = SensorRig(name='A vehicle sensor rig', description={'T': [0.0]*12})
camera_names = ['stereo_left', 'stereo_right', 'left', 'right', 'top']
cameras = [Camera(name=x, description={'P': [0.0]*16}, sensor_rig=sensor_rig) for x in camera_names]

# TODO: get this information from VImap metadata
newmap = Map(name='A test map', description={'T_global': [0.0]*12}, created_at=ts, updated_at=ts)

# TODO: question - use single pose graph or multiple?
pg = PoseGraph(name=vimap.mission, description={'Some_generic_setting': 0.2})
sensor_rig.posegraph = pg
num_vertices = vimap.vertices.shape[0]

pg.map = newmap

poses = [Pose(position=f'POINTZ({vimap.vertices["position_x"][i]} {vimap.vertices["position_y"][i]} {vimap.vertices["position_z"][i]})',
              posegraph=pg) for i in range(num_vertices)]
for i in poses[1:]:
    i.parent = poses[0]

# todo: why is this not linked with landmarks?
num_observations = vimap.observations.shape[0]
observations = []
camera_keypoints = []
for i in range(num_observations):
    # ?? ValueError: Bidirectional attribute conflict detected: Passing object <Camera at 0x7f5700aec250>
    # to attribute "Observation.pose" triggers a modify event on attribute "Observation.sensor"
    # via the backref "Sensor.observations".
    observations.append(
        CameraObservation(created_at=0,
                          updated_at=0,
                          sensor=cameras[vimap.observations['frame_index'][i]],
                          camera=cameras[vimap.observations['frame_index'][i]])
    )

    pose_tracks = vimap.tracks[vimap.tracks.vertex_index == i]
    pose_observations = vimap.observations[vimap.observations.vertex_index == i]


# TODO: Landmarks
# TODO: Semantic info

session = Session()
session.add_all([newmap, pg, sensor_rig] + cameras + poses + observations)
session.commit()

session.commit()

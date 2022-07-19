import msgpack

from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import with_polymorphic

from geoalchemy2 import Geometry, func

from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import *
from datetime import datetime
from pathlib import Path

msg_pack_file_path = Path(
    "/workspaces/openschema_postgres_utils/data/repacked.msg")

engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', echo=False)

Session = sessionmaker(bind=engine)
session = Session()
maps = session.query(Map)

for map in maps:
    print(f"{map.id}: {map.name}")
    for posegraph in map.posegraphs:
        print(f"  Posegraph: {posegraph.id}")
        # posegraph has exact one sensor_rig
        sensor_rig = posegraph.sensor_rig[0]
        sensors = sensor_rig.sensors
        for sensor in sensors:
            print(f"    sensors: {sensor.id} named {sensor.name}")
        for pose in posegraph.poses:
            print(f"    pose: {pose.id} ; position: {session.execute(func.ST_AsText(pose.position)).scalar()}")
            for observation in pose.observations:
                camera_observation = session.query(CameraObservation).filter(CameraObservation.id == observation.id).first()
                print(f"      camera_observation: {camera_observation.id}")
                for keypoint in camera_observation.keypoints:
                    print(f"        keypoint: {keypoint.id} ; descriptor: {keypoint.descriptor} : point: {session.execute(func.ST_AsText(keypoint.point)).scalar()}")
                    landmark = keypoint.landmark
                    if landmark is not None:
                        print(f"          landmark: {landmark.id} ; point: {session.execute(func.ST_AsText(landmark.position)).scalar()}")
                



    

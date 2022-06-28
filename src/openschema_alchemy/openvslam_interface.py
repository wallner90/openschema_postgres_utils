
import msgpack

from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema

from geoalchemy2 import Geometry, func

from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import *
from datetime import datetime
from pathlib import Path

msg_pack_file_path = Path("/workspaces/openschema_postgres_utils/data/knapp_2022_03_03_dobl_test_env.msg")

with open(msg_pack_file_path, "rb") as data_file:
    loaded_data = msgpack.unpackb(data_file.read(), use_list=False, raw=False)
    # print(loaded_data)


    engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', echo=True)
    if not engine.dialect.has_schema(engine, 'public'):
        engine.execute(CreateSchema('public'))
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    cameras = list(loaded_data['cameras'].keys())
    if len(cameras) != 1:
        print(f"Only setups with one (stereo) camera supportet at the moment, given: {len(cameras)}")
        exit

    camera_name = list(loaded_data["cameras"].keys())[0]

    sensor_rig = SensorRig(name=camera_name+" Rig", description={'T': [0.0]*12})
    camera = Camera(name=camera_name, description={"openVSLAM_config": loaded_data["cameras"][camera_name]}, sensor_rig=sensor_rig)

    ts = datetime.utcnow()
    newmap = Map(name=msg_pack_file_path.name + str(ts), description={"T_global": [0.0]*12}, created_at=ts, updated_at=ts)

    pg = PoseGraph(name="SLAM graph", description={"Some_generic_setting": 0.2})
    sensor_rig.posegraph = pg
    num_vertices = 500

    pg.map = newmap

    poses = [Pose(position=f"POINTZ({2*i} {3*i} {i})", posegraph=pg) for i in range(num_vertices)]
    for i in poses[1:]:
        i.parent = poses[0]

    # TODO: Observations
    # TODO: Landmarks
    # TODO: Semantic info

    session = Session()
    session.add_all([newmap, pg, sensor_rig, camera] + poses)
    session.commit()

    session.commit()



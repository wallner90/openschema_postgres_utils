import msgpack

from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import with_polymorphic

from geoalchemy2 import Geometry, func

from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from openschema_alchemy.model import *
from datetime import datetime
from pathlib import Path

msg_pack_file_path = Path(
    "/workspaces/openschema_postgres_utils/data/repacked.msg")


msg_pack_file_path_cmp = Path(
    "/workspaces/openschema_postgres_utils/data/knapp_2022_03_03_dobl_test_env.msg")

loaded_data_msg_pack_cmp = msgpack.unpackb(
    open(msg_pack_file_path_cmp, "rb").read(), use_list=True, raw=False)


engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', poolclass=QueuePool, echo=False, pool_size=200)

map_name = 'knapp_2022_03_03_dobl_test_env.msg2022-08-02 12:10:43.036200'


Session = sessionmaker(bind=engine)
session = Session()


# Version with queries
all_sensors = session.query(Sensor).join(SensorRig).join(
    PoseGraph).join(Map).filter(Map.name == map_name).all()
all_observations = session.query(Observation).join(Pose).join(
    PoseGraph).join(Map).filter(Map.name == map_name).all()
all_landmarks = session.query(Landmark).join(CameraKeypoint).join(Observation, CameraKeypoint.camera_observation_id ==
                                                                  Observation.id).join(Pose).join(PoseGraph).join(Map).filter(Map.name == map_name).all()
for observation in all_observations:
    pose = observation.pose
    keypoints = observation.keypoints

with open(msg_pack_file_path, "wb") as output_file:
    data = {}
    for sensor in all_sensors:
        cameras = {sensor.name: sensor.description['openVSLAM_config']}
        data['cameras'] = cameras

    # TODO: frame_next_id needs to be checked?
    data['frame_next_id'] = data['keyframe_next_id'] = len(all_observations)
    data['landmark_next_id'] = len(all_landmarks)

    keyframes = {}
    for observation in all_observations:
        kf_idx = str(all_observations.index(observation))
        keyframes[kf_idx] = {'cam': observation.sensor.name,
                             'depth_thr': -1,  # TODO: ADD THIS in algorithm_settings!!!
                             'depths': [],
                             'descs': [],
                             'keypts': [],
                             'lm_ids': [],
                             'loop_edges': [],
                             'n_keypts': len(observation.keypoints),
                             'n_scale_levels': -1,  # TODO: ADD THIS in algorithm_settings!!!
                             'rot_cw': [],
                             'scale_factor': -1,  # TODO: ADD THIS in algorithm_settings!!!
                             'span_children': [],
                             'span_parent': -1,
                             'src_frm_id': -1,
                             'trans_cw': [],
                             'ts': -1,
                             'undist': [],
                             'x_rights': []
                             }
    data['keyframes'] = keyframes

    landmarks = {}
    data['landmarks'] = landmarks

    output_data = msgpack.packb(data)
    output_file.write(output_data)


# Version with loops
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
            print(
                f"    pose: {pose.id} ; position: {session.execute(func.ST_AsText(pose.position)).scalar()}")
            for observation in pose.observations:
                camera_observation = session.query(CameraObservation).filter(
                    CameraObservation.id == observation.id).first()
                print(f"      camera_observation: {camera_observation.id}")
                for keypoint in camera_observation.keypoints:
                    print(
                        f"        keypoint: {keypoint.id} ; descriptor: {keypoint.descriptor} : point: {session.execute(func.ST_AsText(keypoint.point)).scalar()}")
                    landmark = keypoint.landmark
                    if landmark is not None:
                        print(
                            f"          landmark: {landmark.id} ; point: {session.execute(func.ST_AsText(landmark.position)).scalar()}")

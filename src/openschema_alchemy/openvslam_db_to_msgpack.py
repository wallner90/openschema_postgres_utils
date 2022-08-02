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

map_name = 'knapp_2022_03_03_dobl_test_env.msg2022-08-02 12:56:14.817110'


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
        depths = []
        x_rights = []
        keypoints = []
        descs = []
        lm_ids = []
        for keypoint in observation.camera_keypoints:
            depths.append(keypoint.descriptor['openVSLAM']['depth'])
            x_rights.append(keypoint.descriptor['openVSLAM']['x_right'])
            keypoints.append({'ang': keypoint.descriptor['openVSLAM']['ang'],
                              'oct': keypoint.descriptor['openVSLAM']['oct'],
                              'pt': [session.execute(func.ST_X(keypoint.point)).scalar(),
                                     session.execute(func.ST_Y(keypoint.point)).scalar()]})
            descs.append(keypoint.descriptor['openVSLAM']['ORB'])
            lm_ids.append(all_landmarks.index(keypoint.landmark)
                          if keypoint.landmark in all_landmarks else -1)

        span_children = [all_observations.index(x) if x in all_observations else None
                         for x in session.query(Observation)
                                         .join(BetweenEdge, Observation.id == BetweenEdge.to_observation_id)
                                         .filter(BetweenEdge.edge_info == None)
                                         .filter(BetweenEdge.from_observation_id == observation.id).all()]

        span_parent = [all_observations.index(x) if x in all_observations else None
                       for x in session.query(Observation)
                                       .join(BetweenEdge, Observation.id == BetweenEdge.from_observation_id)
                                       .filter(BetweenEdge.edge_info == None)
                                       .filter(BetweenEdge.to_observation_id == observation.id).all()]

        loop_edges = [all_observations.index(x) if x in all_observations else None
                      for x in session.query(Observation)
                                      .join(BetweenEdge, Observation.id == BetweenEdge.to_observation_id)
                                      .filter(text("(edge_info->>'is_edge')::boolean = true"))
                                      .filter(BetweenEdge.from_observation_id == observation.id).all()]

        keyframes[kf_idx] = {'cam': observation.sensor.name,
                             'depth_thr': observation.algorithm_settings['openVSLAM']['depth_thr'],
                             'depths': depths,
                             'descs': descs,
                             'keypts': keypoints,
                             'lm_ids': lm_ids,
                             'loop_edges': loop_edges,
                             'n_keypts': len(observation.keypoints),
                             'n_scale_levels': observation.algorithm_settings['openVSLAM']['n_scale_levels'],
                             'rot_cw': [],
                             'scale_factor': observation.algorithm_settings['openVSLAM']['scale_factor'],
                             'span_children': span_children,
                             'span_parent': -1 if len(span_parent) == 0 else span_parent[0],
                             'src_frm_id': 0,
                             'trans_cw': [session.execute(func.ST_X(observation.pose.position)).scalar(),
                                          session.execute(func.ST_Y(observation.pose.position)).scalar(),
                                          session.execute(func.ST_Z(observation.pose.position)).scalar()],
                             'ts': (observation.updated_at-datetime(1970,1,1)).total_seconds(),
                             'undist': [],
                             'x_rights': x_rights
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

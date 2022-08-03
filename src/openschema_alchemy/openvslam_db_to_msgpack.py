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

from math import sin, cos

from tqdm import tqdm


def euler_to_quaternion(roll, pitch, yaw):
    cy = cos(yaw * 0.5)
    sy = sin(yaw * 0.5)
    cp = cos(pitch * 0.5)
    sp = sin(pitch * 0.5)
    cr = cos(roll * 0.5)
    sr = sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return [qw, qx, qy, qz]


msg_pack_file_path = Path(
    "/workspaces/openschema_postgres_utils/data/repacked.msg")


msg_pack_file_path_cmp = Path(
    "/workspaces/openschema_postgres_utils/data/knapp_2022_03_03_dobl_test_env.msg")

loaded_data_msg_pack_cmp = msgpack.unpackb(
    open(msg_pack_file_path_cmp, "rb").read(), use_list=True, raw=False)


engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', poolclass=QueuePool, echo=False, pool_size=200)

map_name = 'knapp_2022_03_03_dobl_test_env.msg2022-08-03 10:15:05.602374'


Session = sessionmaker(bind=engine)
session = Session()


all_sensors = session.query(Sensor).join(SensorRig).join(
    PoseGraph).join(Map).filter(Map.name == map_name).all()
all_observations = session.query(Observation).join(Pose).join(
    PoseGraph).join(Map).filter(Map.name == map_name).all()
all_landmarks = session.query(Landmark).join(CameraKeypoint).join(Observation, CameraKeypoint.camera_observation_id ==
                                                                  Observation.id).join(Pose).join(PoseGraph).join(Map).filter(Map.name == map_name).all()

with open(msg_pack_file_path, "wb") as output_file:
    data = {}
    for sensor in all_sensors:
        cameras = {sensor.name: sensor.description['openVSLAM_config']}
        data['cameras'] = cameras

    # TODO: frame_next_id needs to be checked?
    data['frame_next_id'] = data['keyframe_next_id'] = len(all_observations)
    data['landmark_next_id'] = len(all_landmarks)

    landmarks = {}
    for landmark in tqdm(all_landmarks, desc="Landmarks"):
        lm_idx = str(all_landmarks.index(landmark))
        landmarks[lm_idx] = {'1st_keyfrm': all_observations.index(landmark.camera_keypoints[0].camera_observation) if len(
            landmark.camera_keypoints) > 0 else -1,
            'n_fnd': len(landmark.camera_keypoints),
            'n_vis': len(landmark.camera_keypoints),
            'pos_w': [session.execute(func.ST_X(landmark.position)).scalar(),
                      session.execute(
                func.ST_Y(landmark.position)).scalar(),
            session.execute(func.ST_Z(landmark.position)).scalar()]
        }
    data['landmarks'] = landmarks

    keyframes = {}
    for observation in tqdm(all_observations, desc="Observations"):
        kf_idx = str(all_observations.index(observation))
        depths = []
        x_rights = []
        keypoints = []
        descs = []
        lm_ids = []
        undist = []
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
            undist.append(keypoint.descriptor['openVSLAM']['undist'])

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
                                      .filter(text("(edge_info->>'is_loop_edge')::boolean = true"))
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
                             'rot_cw': euler_to_quaternion(
                                 roll=session.execute(
                                     func.ST_X(observation.pose.normal)).scalar(),
                                 pitch=session.execute(
                                     func.ST_Y(observation.pose.normal)).scalar(),
                                 yaw=session.execute(func.ST_Z(observation.pose.normal)).scalar()),
                             'scale_factor': observation.algorithm_settings['openVSLAM']['scale_factor'],
                             'span_children': span_children,
                             'span_parent': -1 if len(span_parent) == 0 else span_parent[0],
                             'src_frm_id': 0,
                             'trans_cw': [session.execute(func.ST_X(observation.pose.position)).scalar(),
                                          session.execute(
                                              func.ST_Y(observation.pose.position)).scalar(),
                                          session.execute(func.ST_Z(observation.pose.position)).scalar()],
                             'ts': (observation.updated_at-datetime(1970, 1, 1)).total_seconds(),
                             'undist': undist,
                             'x_rights': x_rights
                             }
    data['keyframes'] = keyframes

    output_data = msgpack.packb(data)
    output_file.write(output_data)


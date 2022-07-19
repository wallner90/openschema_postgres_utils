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

msg_pack_file_path = Path(
    "/workspaces/openschema_postgres_utils/data/knapp_2022_03_03_dobl_test_env.msg")

with open(msg_pack_file_path, "rb") as data_file:
    loaded_data = msgpack.unpackb(data_file.read(), use_list=True, raw=False)
    # print(loaded_data)

    engine = create_engine(
        'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', echo=False)
    if not engine.dialect.has_schema(engine, 'public'):
        engine.execute(CreateSchema('public'))
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    cameras = list(loaded_data['cameras'].keys())
    if len(cameras) != 1:
        print(
            f"Only setups with one (stereo) camera supportet at the moment, given: {len(cameras)}")
        exit

    camera_name = list(loaded_data["cameras"].keys())[0]

    sensor_rig = SensorRig(name=camera_name+" Rig",
                           description={"T": [0.0]*12})
    camera = Camera(name=camera_name, description={
                    "openVSLAM_config": loaded_data["cameras"][camera_name]}, sensor_rig=sensor_rig)

    ts = datetime.utcnow()
    newmap = Map(name=msg_pack_file_path.name + str(ts),
                 description={"T_global": [0.0]*12}, created_at=ts, updated_at=ts)

    pg = PoseGraph(name="SLAM graph", map=newmap, description={
                   "Some_generic_setting": 0.2})
    sensor_rig.posegraph = pg

    landmarks = {}
    # Add landmarks
    for landmark_id in list(loaded_data["landmarks"].keys()):
        landmark_msgpack = loaded_data["landmarks"][landmark_id]
        landmark_pos_w = landmark_msgpack["pos_w"]

        landmarks[int(landmark_id)] = Landmark(
            position=f"POINTZ({landmark_pos_w[0]} {landmark_pos_w[1]} {landmark_pos_w[2]})")

    poses = []
    observations = {}
    camera_keypoints = []
    # Add keypoints
    # go over all keyframes
    for keyframe_id in list(loaded_data["keyframes"].keys()):
        keyframe_msgpack = loaded_data["keyframes"][keyframe_id]
        keypts_msgpack = keyframe_msgpack["keypts"]
        lm_ids_msgpack = keyframe_msgpack["lm_ids"]
        descriptors_msgpack = keyframe_msgpack["descs"]
        depths_msgpack = keyframe_msgpack["depths"]
        x_rights = keyframe_msgpack["x_rights"]

        trans_cw = keyframe_msgpack["trans_cw"]
        # TODO: Calculate unit vector from quaternion and add to pose
        pose = Pose(
            position=f"POINTZ({trans_cw[0]} {trans_cw[1]} {trans_cw[2]})",
            posegraph=pg)
        poses.append(pose)

        creation_time = datetime.fromtimestamp(float(keyframe_msgpack["ts"])/1000.0)
        camera_observation = CameraObservation(
            pose=pose, sensor=camera, camera=camera, algorithm="openVSLAM",
            created_at = creation_time, 
            updated_at = creation_time)
        observations[int(keyframe_id)] = camera_observation

        for keypt, lm_id, descriptor, depths, x_right in zip(keypts_msgpack, lm_ids_msgpack, descriptors_msgpack, depths_msgpack, x_rights):
            ckp = CameraKeypoint(point=f"POINT({keypt['pt'][0]} {keypt['pt'][1]})",
                                 descriptor=descriptor,
                                 camera_observation=camera_observation)
            if lm_id != -1 and int(lm_id) in landmarks.keys():
                ckp.landmark = landmarks[int(lm_id)]
            camera_keypoints.append(ckp)
    


        
    session = Session()
    session.add_all([newmap, pg, sensor_rig, camera] +
                    list(landmarks.values()) +
                    camera_keypoints + poses + list(observations.values()))
    session.commit()

    # TODO: adding CameraObservation as Observation is not possible direct -> need to add id manually -> need to commit first to get an ID
    # Maybe there is a more elgant way to use the automatic deduction of dependencies with inheritence / upcast? E.g., observation_id = Observation(current_observation).
    edges = []
    # Add (covisibility and loop) edges
    for keyframe_id in list(loaded_data["keyframes"].keys()):
        keyframe_msgpack = loaded_data["keyframes"][keyframe_id]
        current_observation = observations[int(keyframe_id)]
        for child_keyframe_id in keyframe_msgpack['span_children']:
            child_observation = observations[child_keyframe_id]
            edges.append(BetweenEdge(from_observation_id = current_observation.id, to_observation_id = child_observation.id))

        for loop_edge_id in keyframe_msgpack['loop_edges']:
            child_observation = observations[loop_edge_id]
            edges.append(BetweenEdge(from_observation_id = current_observation.id, to_observation_id = child_observation.id, edge_info = {"is_edge": True}))

    session.add_all(edges)
    session.commit()

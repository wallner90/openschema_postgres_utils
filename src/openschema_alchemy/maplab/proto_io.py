import json
import numpy as np
from google.protobuf.json_format import MessageToJson
from datetime import datetime
from scipy.spatial.transform import Rotation
from tqdm.asyncio import tqdm

from maplab.vimap.proto import VIMap
from model import Landmark, Map, PoseGraph, SensorRig, Camera, IMU, Pose, CameraObservation, CameraKeypoint


def to_db(session, input_dir, map_name):
    vimap = VIMap(input_dir)

    # TODO: database upload time or map measurement allocation time?
    time = datetime.utcnow()
    dp_map = Map(name=map_name, description={'type': 'vimap'}, created_at=time, updated_at=time)

    db_posegraph = PoseGraph(name='vimap graph', description={'mission': MessageToJson(vimap.message.missions[0])},
                             map=dp_map)
    # collect sensors
    db_sensor_rig = SensorRig(name='sensor rig', description={'config': json.dumps(vimap.sensors)},
                              posegraph=db_posegraph)
    db_cameras = []
    db_imus = []
    for sensor in vimap.sensors['sensors']:
        sensor_type = sensor['sensor_type']
        if sensor_type == 'NCAMERA':
            print('Found camera')
            for s in sensor['cameras']:
                camera = s['camera']
                db_cameras.append(
                    Camera(name=camera['topic'], description={'id': camera['id']}, sensor_rig=db_sensor_rig))
        if sensor_type == 'IMU':
            print('Found imu')
            db_imus.append(IMU(name=sensor['topic'], description={'id': sensor['id']}, sensor_rig=db_sensor_rig))

    # collect poses and landmarks
    poses = vimap.message.vertices
    pose_ids = vimap.message.vertex_ids
    db_poses = {}
    db_landmarks = {}
    landmark_quality_filter = [0, 1, 2]  # 0 = unknown, 1 = bad, 2 = good
    for pose, pose_id in zip(poses, pose_ids):
        pose_transform = np.array(pose.T_M_I)
        pose_quaternion = pose_transform[0:4]
        pose_position = pose_transform[4:7]
        pose_rotvec = Rotation.from_quat(pose_quaternion).as_rotvec()
        db_pose = Pose(position=f'POINTZ({pose_position[0]} {pose_position[1]} {pose_position[2]})',
                       rotation_vector=f'POINTZ({pose_rotvec[0]} {pose_rotvec[1]} {pose_rotvec[2]})',
                       posegraph=db_posegraph)
        db_poses[pose_id.uint[1]] = db_pose
        landmarks = pose.landmark_store.landmarks
        for landmark in landmarks:
            if landmark.quality in landmark_quality_filter:
                # we need to transform the landmark position from local to global coordinate frame
                # TODO: apply transform of mission frame
                local_pos = np.array(landmark.position)
                global_pos = Rotation.from_quat(pose_quaternion).apply(local_pos) + pose_position
                db_landmarks[landmark.id.uint[1]] = \
                    Landmark(position=f'POINTZ({global_pos[0]} {global_pos[1]} {global_pos[2]})')

    # collect camera keypoints
    db_camera_keypoints = []
    print("Loading camera keypoints: ")
    for pose, pose_id in tqdm(zip(poses, pose_ids), total=len(poses)):
        frames = pose.n_visual_frame.frames
        assert len(frames) == len(db_cameras), "Error: Assumed lengths are equal."
        for camera, frame in zip(db_cameras, frames):
            # TODO: conversion looses precision (from nano seconds to micro seconds)!
            time = datetime.fromtimestamp(float(frame.timestamp) / 10 ** 9)
            db_camera_observation = CameraObservation(pose=db_poses[pose_id.uint[1]], sensor=camera, camera=camera,
                                                      algorithm="rovisoli", created_at=time, updated_at=time)
            keypoint_num = len(frame.keypoint_measurement_sigmas)
            keypoint_positions = np.array(frame.keypoint_measurements).reshape(keypoint_num, 2)
            keypoint_descriptors = np.frombuffer(frame.keypoint_descriptors, dtype=np.uint8) \
                .reshape(keypoint_num, frame.keypoint_descriptor_size)
            for position, descriptor, lm_id in zip(keypoint_positions, keypoint_descriptors, frame.landmark_ids):
                if lm_id.uint[1] in db_landmarks.keys():
                    db_camera_keypoints.append(CameraKeypoint(point=f"POINT({position[0]} {position[1]})",
                                                              descriptor=json.dumps(descriptor.tolist()),
                                                              observation=db_camera_observation,
                                                              landmark=db_landmarks[lm_id.uint[1]]))

    print("Add map structure to database.")
    session.add_all(db_camera_keypoints)
    print("Commit map structure to database.")
    session.commit()

    # TODO: add imu, loop closures, co-visibilities of observations as edges in db - currently not exported to csv!

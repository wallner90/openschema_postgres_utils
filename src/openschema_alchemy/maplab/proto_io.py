import json
import numpy as np
from datetime import datetime
from scipy.spatial.transform import Rotation
from tqdm.asyncio import tqdm

from maplab.vimap.proto import VIMap, tuple_from_id, hex_string_from_tuple
from model import Landmark, Map, PoseGraph, SensorRig, Camera, IMU, Pose, CameraObservation, CameraKeypoint


def to_db(session, input_dir, map_name):
    vimap = VIMap(input_dir)

    # TODO: database upload time or map measurement allocation time?
    time = datetime.utcnow()
    dp_map = Map(name=map_name, description={'type': 'vimap'}, created_at=time, updated_at=time)

    # TODO: multiple missions, now only the first mission is used
    mission, mission_id = vimap.message.missions[0], tuple_from_id(vimap.message.mission_ids[0])
    print(f"Collect data for mission (id: {mission_id})")
    db_posegraph = PoseGraph(name='vimap graph', description={'mission id': json.dumps(mission_id)}, map=dp_map)
    # collect sensors
    db_sensor_rig = SensorRig(name='sensor rig', description={'config': json.dumps(vimap.sensors)},
                              posegraph=db_posegraph)
    db_cameras = []
    db_imus = []
    for sensor in vimap.sensors['sensors']:
        sensor_type = sensor['sensor_type']
        sensor_id = sensor['id']
        if sensor_type == 'NCAMERA':
            if sensor_id == hex_string_from_tuple(tuple_from_id(mission.ncamera_id)):
                print('Found n-camera')
                for s in sensor['cameras']:
                    db_camera = s['camera']
                    db_cameras.append(
                        Camera(name=db_camera['topic'], description={'id': db_camera['id']}, sensor_rig=db_sensor_rig))
        if sensor_type == 'IMU':
            if sensor_id == hex_string_from_tuple(tuple_from_id(mission.imu_id)):
                print('Found imu')
                db_imus.append(IMU(name=sensor['topic'], description={'id': sensor['id']}, sensor_rig=db_sensor_rig))

    # collect poses and landmarks
    vertices = vimap.vertices()
    db_poses = {}
    db_landmarks = {}
    landmark_quality_filter = [0, 1, 2]  # 0 = unknown, 1 = bad, 2 = good
    for pose_id, pose in vertices.items():
        pose_transform = np.array(pose.T_M_I)
        pose_quaternion = pose_transform[0:4]
        pose_position = pose_transform[4:7]
        pose_rotvec = Rotation.from_quat(pose_quaternion).as_rotvec()
        db_pose = Pose(position=f'POINTZ({pose_position[0]} {pose_position[1]} {pose_position[2]})',
                       rotation_vector=f'POINTZ({pose_rotvec[0]} {pose_rotvec[1]} {pose_rotvec[2]})',
                       posegraph=db_posegraph)
        db_poses[pose_id] = db_pose
        landmarks = pose.landmark_store.landmarks
        for landmark in landmarks:
            if landmark.quality in landmark_quality_filter:
                # we need to transform the landmark position from local to global coordinate frame
                # TODO: apply transform of mission frame
                local_pos = np.array(landmark.position)
                global_pos = Rotation.from_quat(pose_quaternion).apply(local_pos) + pose_position
                db_landmarks[tuple_from_id(landmark.id)] = \
                    Landmark(position=f'POINTZ({global_pos[0]} {global_pos[1]} {global_pos[2]})')

    # collect camera keypoints for keyframes of the mission
    db_camera_keypoints = []
    print("Loading camera keypoints: ")
    for pose_id, pose in tqdm(vertices.items(), total=len(vertices)):
        if mission_id != tuple_from_id(pose.mission_id):
            continue
        frames = pose.n_visual_frame.frames
        assert len(frames) == len(db_cameras), f"Error: Assumed lengths are equal, but got {len(frames)} != {len(db_cameras)}."
        for db_camera, frame in zip(db_cameras, frames):
            # TODO: conversion looses precision (from nano seconds to micro seconds)!
            time = datetime.fromtimestamp(float(frame.timestamp) / 10 ** 9)
            db_camera_observation = CameraObservation(pose=db_poses[pose_id], sensor=db_camera, camera=db_camera,
                                                      algorithm="rovisoli", created_at=time, updated_at=time)
            keypoint_num = len(frame.keypoint_measurement_sigmas)
            keypoint_positions = np.array(frame.keypoint_measurements).reshape(keypoint_num, 2)
            keypoint_descriptors = np.frombuffer(frame.keypoint_descriptors, dtype=np.uint8) \
                .reshape(keypoint_num, frame.keypoint_descriptor_size)
            for position, descriptor, lm_id in zip(keypoint_positions, keypoint_descriptors, frame.landmark_ids):
                if tuple_from_id(lm_id) in db_landmarks.keys():
                    db_camera_keypoints.append(CameraKeypoint(point=f"POINT({position[0]} {position[1]})",
                                                              descriptor=json.dumps(descriptor.tolist()),
                                                              observation=db_camera_observation,
                                                              landmark=db_landmarks[tuple_from_id(lm_id)]))

    print("Add map structure to database.")
    session.add_all(db_camera_keypoints)
    print("Commit map structure to database.")
    session.commit()

    # TODO: add imu, loop closures, co-visibilities of observations as edges in db - currently not exported to csv!

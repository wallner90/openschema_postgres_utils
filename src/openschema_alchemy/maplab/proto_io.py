import json
import numpy as np
from datetime import datetime
from scipy.spatial.transform import Rotation
from tqdm.asyncio import tqdm
from uuid import UUID
from maplab.vimap.proto import VIMap, uuid_from_aslam_id
from model import Landmark, Map, PoseGraph, SensorRig, Camera, IMU, Pose, CameraObservation, CameraKeypoint


def to_db(session, input_dir, map_name):
    vimap = VIMap(input_dir)

    # TODO: database upload time or map measurement allocation time?
    time = datetime.utcnow()
    dp_map = Map(name=map_name, description={'type': 'vimap'}, created_at=time, updated_at=time)

    # TODO: multiple missions, now only the first mission is used
    mission, mission_id = vimap.message.missions[0], uuid_from_aslam_id(vimap.message.mission_ids[0])
    print(f"Collect data for mission (id: {mission_id})")
    db_posegraph = PoseGraph(id=mission_id, name='vimap graph',
                             description={'root_vertex_id': uuid_from_aslam_id(mission.root_vertex_id).hex}, map=dp_map)
    # collect sensors
    # Note: we allow exactly one NCAMERA per sensor rig.
    # Therefore, the sensor rig id is set to the NCAMERA id.
    db_sensor_rig = SensorRig(id=uuid_from_aslam_id(mission.ncamera_id),
                              name='sensor rig', description={'config': json.dumps(vimap.sensors)},
                              posegraph=db_posegraph)
    db_cameras = []
    db_imus = []
    for sensor in vimap.sensors['sensors']:
        sensor_type = sensor['sensor_type']
        sensor_id = sensor['id']
        if sensor_type == 'NCAMERA':
            if sensor_id == db_sensor_rig.id.hex:
                print(f"Found {len(sensor['cameras'])}-camera")
                for s in sensor['cameras']:
                    camera = s['camera']
                    db_cameras.append(
                        Camera(id=UUID(hex=camera['id']), name=camera['topic'], description={'ncamera id': sensor_id},
                               sensor_rig=db_sensor_rig))
        if sensor_type == 'IMU':
            if sensor_id == uuid_from_aslam_id(mission.imu_id).hex:
                print('Found imu')
                db_imus.append(IMU(id=UUID(hex=sensor_id), name=sensor['topic'], description={}, sensor_rig=db_sensor_rig))

    # collect poses and landmarks of the mission
    vertices = vimap.vertices()
    db_poses = {}
    db_landmarks = {}
    landmark_quality_filter = [0, 1, 2]  # 0 = unknown, 1 = bad, 2 = good
    for pose_id, pose in vertices.items():
        if mission_id != uuid_from_aslam_id(pose.mission_id):
            continue
        pose_transform = np.array(pose.T_M_I)
        pose_quaternion = pose_transform[0:4]
        pose_position = pose_transform[4:7]
        pose_rotvec = Rotation.from_quat(pose_quaternion).as_rotvec()
        db_pose = Pose(id=pose_id,
                       position=f'POINTZ({pose_position[0]} {pose_position[1]} {pose_position[2]})',
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
                landmark_id = uuid_from_aslam_id(landmark.id)
                db_landmarks[landmark_id] = \
                    Landmark(id=landmark_id,
                             position=f'POINTZ({global_pos[0]} {global_pos[1]} {global_pos[2]})',
                             uncertainty={'covariance': json.dumps([x for x in landmark.covariance])},
                             descriptor={'quality': landmark.quality})

    # collect camera keypoints for keyframes of the mission
    db_camera_keypoints = []
    print("Loading camera keypoints: ")
    for pose_id, pose in tqdm(vertices.items(), total=len(vertices)):
        if mission_id != uuid_from_aslam_id(pose.mission_id):
            continue
        frames = pose.n_visual_frame.frames
        assert len(frames) == len(db_cameras), \
            f"Error: Assumed lengths are equal, but got {len(frames)} != {len(db_cameras)}."
        for db_camera, frame in zip(db_cameras, frames):
            # TODO: conversion looses precision (from nano seconds to micro seconds)!
            time = datetime.fromtimestamp(float(frame.timestamp) / 10 ** 9)
            db_camera_observation = CameraObservation(id=uuid_from_aslam_id(frame.id),
                                                      pose=db_poses[pose_id], sensor=db_camera, camera=db_camera,
                                                      algorithm="maplab feature extractor",
                                                      algorithm_settings={'descriptor_scales': 20,
                                                                          'keypoint_descriptor_size': 48,
                                                                          'keypoint_measurement_sigmas': 0.8},
                                                      created_at=time, updated_at=time)
            keypoint_num = len(frame.keypoint_measurement_sigmas)
            keypoint_positions = np.array(frame.keypoint_measurements).reshape(keypoint_num, 2)
            keypoint_descriptors = np.frombuffer(frame.keypoint_descriptors, dtype=np.uint8) \
                .reshape(keypoint_num, frame.keypoint_descriptor_size)
            for position, descriptor, lm_id in zip(keypoint_positions, keypoint_descriptors, frame.landmark_ids):
                if uuid_from_aslam_id(lm_id) in db_landmarks.keys():
                    db_camera_keypoints.append(CameraKeypoint(point=f"POINT({position[0]} {position[1]})",
                                                              descriptor=json.dumps(descriptor.tolist()),
                                                              observation=db_camera_observation,
                                                              landmark=db_landmarks[uuid_from_aslam_id(lm_id)]))

    print("Add map structure to database.")
    session.add_all(db_camera_keypoints)
    print("Commit map structure to database.")
    session.commit()

    # TODO: add imu, loop closures, co-visibilities of observations as edges in db - currently not exported to csv!

import os
from datetime import datetime

from scipy.spatial.transform import Rotation
from sqlalchemy import func, select
from tqdm.asyncio import tqdm

from maplab.vimap.csv import VImap
from model import SensorRig, Camera, CameraObservation, Map, PoseGraph, Landmark, Pose, CameraKeypoint, Sensor, \
    Observation


def to_db(session, input_dir, map_name):
    vimap = VImap(input_dir)

    # TODO: get this information from VImap metadata
    ts = datetime.utcnow()
    dp_map = Map(name=map_name, description={'T_global': [0.0] * 12}, created_at=ts, updated_at=ts)
    db_posegraph = PoseGraph(name=vimap.mission, description={'Some_generic_setting': 0.2}, map=dp_map)
    # TODO: get this information from config, along with calib!
    db_sensor_rig = SensorRig(name='A vehicle sensor rig', description={'T': [0.0] * 12}, posegraph=db_posegraph)
    camera_names = ['stereo_left', 'stereo_right', 'left', 'right', 'top']
    db_cameras = [Camera(name=name, description={'P': [0.0] * 16}, sensor_rig=db_sensor_rig) for name in camera_names]

    landmark_positions = vimap.landmarks[["landmark_position_x", "landmark_position_y", "landmark_position_z"]].values
    db_landmarks = [Landmark(position=f'POINTZ({pos[0]} {pos[1]} {pos[2]})') for pos in landmark_positions]

    pose_positions = vimap.vertices[["position_x", "position_y", "position_z"]].values
    pose_quaternions = vimap.vertices[["quaternion_x", "quaternion_y", "quaternion_z", "quaternion_w"]].values
    pose_rotation_vectors = Rotation.from_quat(pose_quaternions).as_rotvec()
    db_poses = [Pose(position=f'POINTZ({pos[0]} {pos[1]} {pos[2]})',
                     rotation_vector=f'POINTZ({rvec[0]} {rvec[1]} {rvec[2]})',
                     posegraph=db_posegraph) for pos, rvec in zip(pose_positions, pose_rotation_vectors)]

    db_camera_keypoints = []
    print("Scan keyframes:")
    for keyframe_index in tqdm(vimap.vertices.index):
        # restrict observations to current keyframe
        observations_at_keyframe = vimap.observations[vimap.observations['vertex_index'] == keyframe_index]

        # get all camera indices which observed a landmark at current keyframe
        camera_indices = observations_at_keyframe['frame_index'].unique()
        for camera_index in camera_indices:
            camera = db_cameras[camera_index]

            # TODO: conversion looses precision (from nano seconds to micro seconds)!
            creation_time = datetime.fromtimestamp(float(vimap.vertices["timestamp"][keyframe_index]) / 10**9)

            # get all keypoints and landmarks observed at current keyframe in camera
            keypoints_in_camera_at_keyframe = observations_at_keyframe[
                observations_at_keyframe['frame_index'] == camera_index]
            landmarks_observed_in_camera_at_keyframe = vimap.landmarks[
                vimap.landmarks['landmark_index'].isin(keypoints_in_camera_at_keyframe['landmark_index'])]

            # get associated tracks and descriptors of keypoints
            keypoint_ids_in_camera_at_keyframe = \
                (vimap.keypoint_tracks.vertex_index == keyframe_index)\
                & (vimap.keypoint_tracks.frame_index == camera_index)\
                & (vimap.keypoint_tracks.keypoint_index.isin(keypoints_in_camera_at_keyframe.keypoint_index))
            tracks_in_camera_at_keyframe = vimap.keypoint_tracks[keypoint_ids_in_camera_at_keyframe]
            descriptors = vimap.descriptor[keypoint_ids_in_camera_at_keyframe]

            db_camera_observation = CameraObservation(pose=db_poses[keyframe_index], sensor=camera, camera=camera,
                                                      algorithm="rovisoli",
                                                      created_at=creation_time, updated_at=creation_time)

            assert len(tracks_in_camera_at_keyframe) == len(landmarks_observed_in_camera_at_keyframe),\
                f"[Error: Data inconsistency] Array lengths are not equal:" \
                f" {len(tracks_in_camera_at_keyframe)} != {len(landmarks_observed_in_camera_at_keyframe)}"
            for lm_id, pos_x, pos_y, track_id, descr in zip(landmarks_observed_in_camera_at_keyframe['landmark_index'],
                                                            tracks_in_camera_at_keyframe['keypoint_measurement_0'],
                                                            tracks_in_camera_at_keyframe['keypoint_measurement_1'],
                                                            tracks_in_camera_at_keyframe['keypoint_track_id'],
                                                            descriptors.iterrows()):
                db_camera_keypoints.append(CameraKeypoint(point=f"POINT({pos_x} {pos_y})", descriptor=descr[1][0],
                                                          observation=db_camera_observation,
                                                          landmark=db_landmarks[lm_id]))
    print("Add map structure to database.")
    session.add_all(db_camera_keypoints)
    print("Commit map structure to database.")
    session.commit()

    # TODO: add imu, loop closures, co-visibilities of observations as edges in db - currently not exported to csv!


def to_file(session, output_dir, map_name):
    query_maps = session.query(Map).filter(Map.name == map_name)
    if len(query_maps.all()) == 0:
        print(f"Map named '{map_name}' not found!")
        return

    map_dir = output_dir + "/" + map_name
    if not os.path.exists(map_dir):
        print(f"Create map directory: {map_dir}")
        os.mkdir(map_dir)

    query_posegraphs = session.query(PoseGraph).join(query_maps)
    print(f"Number of missions: {len(query_posegraphs.all())}")
    for mission in query_posegraphs.all():
        mission_dir = map_dir + "/" + mission.name
        if not os.path.exists(mission_dir):
            print(f"Create mission directory: {mission_dir}")
            os.mkdir(mission_dir)

    query_poses = session.query(Pose).join(query_posegraphs)
    print(f"Found {len(query_poses.all())} poses.")
    pose_index = {}
    for keypoint_idx, pose in enumerate(query_poses.all()):
        pose_index[pose.id] = keypoint_idx

    query_sensors = session.query(Sensor).join(SensorRig).join(query_posegraphs)
    sensor_index = {}
    for keypoint_idx, sensor in enumerate(query_sensors.all()):
        sensor_index[sensor.id] = keypoint_idx
        query_camera_observations = session.query(CameraObservation).filter(Observation.sensor_id == sensor.id)
        print(f"Camera {keypoint_idx} has {len(query_camera_observations.all())} observations.")

    query_landmarks = session.query(Landmark)
    print(f"Found {len(query_landmarks.all())} landmarks.")
    landmark_index = {}
    for keypoint_idx, landmark in enumerate(query_landmarks.all()):
        landmark_index[landmark.id] = keypoint_idx

    print("Export: vertices.csv, observations.csv, tracks.csv, descriptor.csv")
    vertices_file = open(mission_dir + "/" + "vertices.csv", "w")
    vertices_file.write("vertex index, timestamp[ns], position x[m], position y[m], position z[m], " \
                        "quaternion x, quaternion y, quaternion z, quaternion w, " \
                        "velocity x[m / s], velocity y[m / s], velocity z[m / s], " \
                        "acc bias x[m / s ^ 2], acc bias y[m / s ^ 2], acc bias z[m / s ^ 2], " \
                        "gyro bias x[rad / s], gyro bias y[rad / s], gyro bias z[rad / s]\n")
    observations_file = open(mission_dir + "/" + "observations.csv", "w")
    observations_file.write("vertex index, frame index, keypoint index, landmark index\n")
    tracks_file = open(mission_dir + "/" + "tracks.csv", "w")
    tracks_file.write("timestamp [ns], vertex index, frame index, keypoint index, "
                      "keypoint measurement 0 [px], keypoint measurement 1 [px], keypoint measurement uncertainty, "
                      "keypoint tag id, keypoint scale, keypoint track id\n")
    descriptor_file = open(mission_dir + "/" + "descriptor.csv", "w")
    descriptor_file.write("Descriptor byte as integer 1-N\n")
    # iterate over poses (key frames)
    for pose in tqdm(query_poses.all()):
        vertex_idx = pose_index[pose.id]
        pose_position = (session.execute(func.ST_X(pose.position)).scalar(),
                         session.execute(func.ST_Y(pose.position)).scalar(),
                         session.execute(func.ST_Z(pose.position)).scalar())
        pose_quat = Rotation.from_rotvec((session.execute(func.ST_X(pose.rotation_vector)).scalar(),
                                          session.execute(func.ST_Y(pose.rotation_vector)).scalar(),
                                          session.execute(func.ST_Z(pose.rotation_vector)).scalar())).as_quat()

        for sensor in query_sensors.all():
            frame_idx = sensor_index[sensor.id]
            camera_observations = session.query(CameraObservation).filter(Observation.sensor_id == sensor.id)\
                .join(Pose).filter(Pose.id == pose.id).all()
            if len(camera_observations) == 0:
                continue
            assert len(camera_observations) == 1, \
                f"Error: It is expected exactly one camera observation with frame_idx={frame_idx} at vertex_idx={vertex_idx}, but got {len(camera_observations)}."
            timestamp = int(datetime.timestamp(camera_observations[0].updated_at)*10**9)
            # vertices.csv:
            if frame_idx == 0:
                # TODO: velocity is missing.
                vertices_file.write(f"{vertex_idx}, {timestamp}, "
                                    f"{pose_position[0]}, {pose_position[1]}, {pose_position[2]}, "
                                    f"{pose_quat[0]}, {pose_quat[1]}, {pose_quat[2]}, {pose_quat[3]}, "
                                    f" 0, 0, 0, "
                                    f"0, 0, 0, 0, 0, 0\n")

            query_keypoints_in_camera_at_keyframe = session.query(CameraKeypoint)\
                .join(CameraObservation).filter(Observation.sensor_id == sensor.id)\
                .join(Pose).filter(Pose.id == pose.id)
            for keypoint_idx, keypoint in enumerate(query_keypoints_in_camera_at_keyframe.all()):
                # observations.csv:
                # vertex index, frame index, keypoint index, landmark index
                landmark_idx = landmark_index[keypoint.landmark_id]
                observations_file.write(f"{vertex_idx}, {frame_idx}, {keypoint_idx}, {landmark_idx}\n")
                # tracks.csv:
                # timestamp [ns], vertex index, frame index, keypoint index,
                # keypoint measurement 0 [px], keypoint measurement 1 [px], keypoint measurement uncertainty,
                # keypoint tag id, keypoint scale, keypoint track id
                keypoint_msr = (int(session.execute(func.ST_X(keypoint.point)).scalar()),
                                int(session.execute(func.ST_Y(keypoint.point)).scalar()))
                tracks_file.write(f"{timestamp}, {vertex_idx}, {frame_idx}, {keypoint_idx}, "
                                  f"{keypoint_msr[0]}, {keypoint_msr[1]}, 0.8, -1, 20, {landmark_idx}\n")
                # descriptor.csv:
                # Descriptor byte as integer 1-N
                descriptor_file.write(f"{keypoint.descriptor}")
    for file in [vertices_file, observations_file, tracks_file, descriptor_file]:
        file.close()

    print("Export: landmarks.csv")

    with open(mission_dir + "/" + "landmarks.csv", "w") as file:
        file.write("landmark index, landmark position x [m], landmark position y [m], landmark position z [m]\n")
        for landmark in tqdm(query_landmarks.all()):
            file.write(f"{landmark_index[landmark.id]}, "
                       f"{session.execute(func.ST_X(landmark.position)).scalar()}, "
                       f"{session.execute(func.ST_Y(landmark.position)).scalar()}, "
                       f"{session.execute(func.ST_Z(landmark.position)).scalar()}\n")

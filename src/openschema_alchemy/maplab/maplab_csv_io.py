from datetime import datetime
from scipy.spatial.transform import Rotation
from .vimap import VImap
from model import SensorRig, Camera, CameraObservation, Map, PoseGraph, Landmark, Pose, CameraKeypoint


def to_db(session, input_dir, map_name):
    vimap = VImap(input_dir)

    m = session.query(Map).filter(Map.name == map_name).all()
    for e in m:
        session.delete(e)
    session.commit()

    # TODO: get this information from VImap metadata
    ts = datetime.utcnow()
    dp_map = Map(name=map_name, description={'T_global': [0.0] * 12}, created_at=ts, updated_at=ts)
    db_posegraph = PoseGraph(name=vimap.mission, description={'Some_generic_setting': 0.2}, map=dp_map)
    # TODO: get this information from config, along with calib!
    db_sensor_rig = SensorRig(name='A vehicle sensor rig', description={'T': [0.0] * 12}, posegraph=db_posegraph)
    camera_names = ['stereo_left', 'stereo_right', 'left', 'right', 'top']
    db_cameras = [Camera(name=x, description={'P': [0.0] * 16}, sensor_rig=db_sensor_rig) for x in camera_names]

    landmark_positions = vimap.landmarks[["landmark_position_x", "landmark_position_y", "landmark_position_z"]].values
    db_landmarks = [Landmark(position=f'POINTZ({p[0]} {p[1]} {p[2]})') for p in landmark_positions]

    pose_positions = vimap.vertices[["position_x", "position_y", "position_z"]].values
    pose_quaternions = vimap.vertices[["quaternion_x", "quaternion_y", "quaternion_z", "quaternion_w"]].values
    pose_rotation_vectors = Rotation.from_quat(pose_quaternions).as_rotvec()
    db_poses = [Pose(position=f'POINTZ({p[0]} {p[1]} {p[2]})',
                     rotation_vector=f'POINTZ({rv[0]} {rv[1]} {rv[2]})',
                     posegraph=db_posegraph) for p, rv in zip(pose_positions, pose_rotation_vectors)]

    db_observations = []
    db_camera_keypoints = []

    for keyframe_index in vimap.vertices.index:
        # restrict observations to current keyframe
        observations_at_keyframe = vimap.observations[vimap.observations['vertex_index'] == keyframe_index]

        # get all camera indices which observed a landmark at current keyframe
        camera_indices = observations_at_keyframe['frame_index'].unique()
        for camera_index in camera_indices:
            camera = db_cameras[camera_index]

            # creation time TODO: this is not correct, get start time from ts!
            creation_time = datetime.fromtimestamp(float(vimap.vertices["timestamp"][keyframe_index]) / 1000000000)

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
            db_observations.append(db_camera_observation)

        session.add_all(db_camera_keypoints)
        # TODO: if the above is sufficient remove the line below
        #    [dp_map, db_sensor_rig.posegraph, db_sensor_rig] + db_cameras + db_landmarks + db_camera_keypoints + db_poses + db_observations)
        session.commit()

def to_file(session, output_dir, map_name):
    print('reading database')

        # TODO: add loop closures, co-visibilities of observations as edges in db - currently not exported to csv!

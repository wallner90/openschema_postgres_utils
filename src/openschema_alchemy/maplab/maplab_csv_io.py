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

    # TODO: get this information from config, along with calib!
    sensor_rig = SensorRig(name='A vehicle sensor rig', description={'T': [0.0] * 12})
    camera_names = ['stereo_left', 'stereo_right', 'left', 'right', 'top']
    cameras = [Camera(name=x, description={'P': [0.0] * 16}, sensor_rig=sensor_rig) for x in camera_names]

    # TODO: get this information from VImap metadata
    ts = datetime.utcnow()
    newmap = Map(name=map_name, description={'T_global': [0.0] * 12}, created_at=ts, updated_at=ts)

    sensor_rig.posegraph = PoseGraph(name=vimap.mission, description={'Some_generic_setting': 0.2})

    landmark_positions = vimap.landmarks[["landmark_position_x", "landmark_position_y", "landmark_position_z"]].values
    landmarks = [Landmark(position=f'POINTZ({p[0]} {p[1]} {p[2]})') for p in landmark_positions]

    pose_positions = vimap.vertices[["position_x", "position_y", "position_z"]].values
    pose_quaternions = vimap.vertices[["quaternion_x", "quaternion_y", "quaternion_z", "quaternion_w"]].values
    pose_rotation_vectors = Rotation.from_quat(pose_quaternions).as_rotvec()
    poses = [Pose(position=f'POINTZ({p[0]} {p[1]} {p[2]})',
                  rotation_vector=f'POINTZ({rv[0]} {rv[1]} {rv[2]})',
                  posegraph=sensor_rig.posegraph) for p, rv in zip(pose_positions, pose_rotation_vectors)]

    observations = {}
    camera_keypoints = []

    for i in vimap.vertices.index:
        # gather all keypoints observed at the current vertex
        observations_from_vertex = vimap.observations[vimap.observations.vertex_index == i]

        camera_indices = observations_from_vertex['frame_index'].unique()
        for camera_index in camera_indices:
            camera = cameras[camera_index]

            # creation time TODO: this is not correct, get start time from ts!
            creation_time = datetime.fromtimestamp(float(vimap.vertices["timestamp"][i]) / 1000000000)

            # create observation TODO: this overrides camera observation from previous camera
            camera_observation = CameraObservation(pose=poses[i], sensor=camera, camera=camera, algorithm="openVSLAM",
                                                   created_at=creation_time, updated_at=creation_time)
            observations[i] = camera_observation

            # gather all keypoints observed at the current vertex
            observations_from_vertex = vimap.observations[
                (vimap.observations.vertex_index == i) & (vimap.observations.frame_index == camera_index)]
            observed_landmarks = \
            vimap.landmarks[['landmark_index', 'landmark_position_x', 'landmark_position_y', 'landmark_position_z']][
                vimap.landmarks.landmark_index.isin(observations_from_vertex.landmark_index)]

            # align descriptors to image keypoints
            tracks = vimap.keypoint_tracks[(vimap.keypoint_tracks.vertex_index == i) & (vimap.keypoint_tracks.frame_index == camera_index) & (
                vimap.keypoint_tracks.keypoint_index.isin(observations_from_vertex.keypoint_index))]
            descriptors = vimap.descriptor[(vimap.keypoint_tracks.vertex_index == i) & (vimap.keypoint_tracks.frame_index == camera_index) &
                                           (vimap.keypoint_tracks.keypoint_index.isin(observations_from_vertex.keypoint_index))]

            for x, y, track_id, descr, lms_ind in zip(tracks['keypoint_measurement_0'],
                                                      tracks['keypoint_measurement_1'], tracks['keypoint_track_id'],
                                                      descriptors, observed_landmarks['landmark_index']):
                ckp = CameraKeypoint(point=f"POINT({x} {y})", descriptor=descr, observation=camera_observation,
                                     landmark=landmarks[lms_ind])
                camera_keypoints.append(ckp)
        session.add_all(
            [newmap, sensor_rig.posegraph, sensor_rig] + cameras + landmarks + camera_keypoints + poses + list(
                observations.values()))
        session.commit()

        # TODO: add loop closures, co-visibilities of observations as edges in db - currently not exported to csv!

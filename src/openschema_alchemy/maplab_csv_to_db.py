from sqlalchemy import create_engine

from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import *
from datetime import datetime

from openschema_alchemy.vi_map import VImap
from pyquaternion import Quaternion


# load vi-map
vimap = VImap('/data/iviso/_OpenSCHEMA/Knapp_Dobl/dobl_halle_tagged/aaadfd42874eeb161400000000000000')


# TODO: Before use pgterm later maybe with sqlalchemy utils
#       CREATE DATABASE IF NOT EXISTS postgres_alchemy_ait;
#       \c postgres_alchemy_ait;
#       CREATE SCHEMA "public";
#       CREATE EXTENSION "postgis";
#       CREATE EXTENSION "uuid-ossp";
# TODO: Time in TAI might be better??
engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', echo=True,
     connect_args={"options": "-c timezone=utc"})
if not engine.dialect.has_schema(engine, 'public'):
    engine.execute(CreateSchema('public'))
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

# TODO: get this information from config, along with calib!
sensor_rig = SensorRig(name='A vehicle sensor rig', description={'T': [0.0]*12})
camera_names = ['stereo_left', 'stereo_right', 'left', 'right', 'top']
cameras = [Camera(name=x, description={'P': [0.0]*16}, sensor_rig=sensor_rig) for x in camera_names]

# TODO: get this information from VImap metadata
ts = datetime.utcnow()
newmap = Map(name='A test map', description={'T_global': [0.0]*12}, created_at=ts, updated_at=ts)

# TODO: question - use single pose graph or multiple?
pg = PoseGraph(name=vimap.mission, description={'Some_generic_setting': 0.2})
sensor_rig.posegraph = pg
num_vertices = vimap.vertices.shape[0]

pg.map = newmap


landmarks = {}
# Add landmarks
for i in range(vimap.landmarks.shape[0]):
    landmarks[int(vimap.landmarks.landmark_index[i])] = Landmark(
        position=f"POINTZ("
                 f"{vimap.landmarks.landmark_position_x[i]} "
                 f"{vimap.landmarks.landmark_position_y[i]} "
                 f"{vimap.landmarks.landmark_position_z[i]})")

# Go over poses, add observations
observations = {}
camera_keypoints = []

# TODO - direction as quaternion instead?
poses = [Pose(position=f'POINTZ({vimap.vertices["position_x"][i]} {vimap.vertices["position_y"][i]} {vimap.vertices["position_z"][i]})',
              posegraph=pg) for i in range(num_vertices)]
for i in range(num_vertices):
    # orientation from pose quaternion
    Q = Quaternion(axis=[vimap.vertices["quaternion_x"][i], vimap.vertices["quaternion_y"][i], vimap.vertices["quaternion_z"][i]],
                   angle=vimap.vertices["quaternion_w"][i])

    x = vimap.vertices["quaternion_x"][i]
    y = vimap.vertices["quaternion_y"][i]
    z = vimap.vertices["quaternion_z"][i]
    w = vimap.vertices["quaternion_w"][i]

    # up vector
    #x = 2 * (x * y - w * z)
    #y = 1 - 2 * (x * x + z * z)
    #z = 2 * (y * z + w * x)

    # left vector
    #x = 1 - 2 * (y * y + z * z)
    #y = 2 * (x * y + w * z)
    #z = 2 * (x * z - w * y)

    # forward vector:
    x = 2 * (x * z + w * y)
    y = 2 * (y * z - w * x)
    z = 1 - 2 * (x * x + y * y)

    poses[i].normal = [x, y, z]

    # gather all keypoints observed at the current vertex
    observations_from_vertex = vimap.observations[vimap.observations.vertex_index == i]


    unique_cams = observations_from_vertex['frame_index'].unique()
    for cam in unique_cams:
        # creation time (TODO: this is not correct, get start time from ts!)
        creation_time = datetime.fromtimestamp(float(vimap.vertices["timestamp"][i]) / 1000000000)

        sensor = cameras[cam]
        camera = cameras[cam]

        # create observation
        camera_observation = CameraObservation(
            pose=poses[i], sensor=camera, camera=camera, algorithm="openVSLAM",
            created_at=creation_time,
            updated_at=creation_time)
        observations[int(i)] = camera_observation

        # gather all keypoints observed at the current vertex
        observations_from_vertex = vimap.observations[(vimap.observations.vertex_index == i) & (vimap.observations.frame_index == cam)]
        observed_landmarks = vimap.landmarks[['landmark_index', 'landmark_position_x', 'landmark_position_y', 'landmark_position_z']][vimap.landmarks.landmark_index.isin(observations_from_vertex.landmark_index)]

        # align descriptors to image keypoints
        tracks = vimap.tracks[(vimap.tracks.vertex_index == i) & (vimap.tracks.frame_index == cam) & (vimap.tracks.keypoint_index.isin(observations_from_vertex.keypoint_index))]
        descrs = vimap.descriptor.to_numpy()[(vimap.tracks.vertex_index == i) & (vimap.tracks.frame_index == cam) & (vimap.tracks.keypoint_index.isin(observations_from_vertex.keypoint_index)), :]

        for x, y, track_id, descr, lms_ind in zip(tracks['keypoint_measurement_0'], tracks['keypoint_measurement_1'], tracks['keypoint_track_id'], descrs,
                                                              observed_landmarks['landmark_index'] ):
            ckp = CameraKeypoint(point=f"POINT({x} {y})", descriptor=descr, camera_observation=camera_observation,
                                 landmark=landmarks[lms_ind])
            camera_keypoints.append(ckp)

    session = Session()
    session.add_all([newmap, pg, sensor_rig, cameras] +
                    list(landmarks.values()) +
                    camera_keypoints + poses + list(observations.values()))
    session.commit()

    # TODO: add loop closures, co-visibilities of observations as edges in db - currently not exported to csv!

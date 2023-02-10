import json
import numpy as np
from datetime import datetime
from scipy.spatial.transform import Rotation
from sqlalchemy import select, func
from tqdm.asyncio import tqdm
from uuid import UUID, uuid4
from maplab.vimap.proto import VIMap, uuid_from_aslam_id, vi_map_pb2, get_edge_type, aslam_id_from_uuid
from model import Landmark, Map, PoseGraph, SensorRig, Camera, IMU, Pose, CameraObservation, CameraKeypoint, \
    BetweenEdge, Observation, ObservationType
from google.protobuf.json_format import MessageToDict, ParseDict


def to_db(session, input_dir, map_name):
    vimap = VIMap(input_dir)

    # TODO: database upload time or map measurement allocation time?
    time = datetime.utcnow()
    dp_map = Map(name=map_name, description={'type': 'vimap'}, created_at=time, updated_at=time)

    # TODO: multiple missions, now only the first mission is used
    mission, mission_id = vimap.message.missions[0], uuid_from_aslam_id(vimap.message.mission_ids[0])
    print(f"Collect data for mission (id: {mission_id})")
    db_posegraph = PoseGraph(id=mission_id, name='vimap graph', description={}, map=dp_map)
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
                db_imus.append(
                    IMU(id=UUID(hex=sensor_id), name=sensor['topic'], description={}, sensor_rig=db_sensor_rig))

    # collect poses and landmarks of the mission
    vertices = vimap.vertices()
    db_poses = {}
    edge_ids = set()
    db_landmarks = {}
    landmark_quality_filter = [0, 1, 2]  # 0 = unknown, 1 = bad, 2 = good
    print("Loading poses and landmarks.")
    for vertex_id, vertex in vertices.items():
        if mission_id != uuid_from_aslam_id(vertex.mission_id):
            continue
        vertex_transform = np.array(vertex.T_M_I)
        vertex_quaternion = vertex_transform[0:4]
        vertex_position = vertex_transform[4:7]
        pose_rotvec = Rotation.from_quat(vertex_quaternion).as_rotvec()
        db_pose = Pose(id=vertex_id,
                       position=f'POINTZ({vertex_position[0]} {vertex_position[1]} {vertex_position[2]})',
                       rotation_vector=f'POINTZ({pose_rotvec[0]} {pose_rotvec[1]} {pose_rotvec[2]})',
                       posegraph=db_posegraph)
        db_poses[vertex_id] = db_pose
        # collect landmarks
        landmarks = vertex.landmark_store.landmarks
        for landmark in landmarks:
            if landmark.quality in landmark_quality_filter:
                # we need to transform the landmark position from local to global coordinate frame
                # TODO: apply transform of mission frame
                local_pos = np.array(landmark.position)
                global_pos = Rotation.from_quat(vertex_quaternion).apply(local_pos) + vertex_position
                landmark_id = uuid_from_aslam_id(landmark.id)
                db_landmarks[landmark_id] = \
                    Landmark(id=landmark_id,
                             position=f'POINTZ({global_pos[0]} {global_pos[1]} {global_pos[2]})',
                             uncertainty={'covariance': json.dumps([x for x in landmark.covariance])},
                             descriptor={'quality': landmark.quality})

    # collect camera keypoints for keyframes of the mission
    db_camera_keypoints = []
    print("Loading camera keypoints: ")
    for vertex_id, vertex in tqdm(vertices.items(), total=len(vertices)):
        if mission_id != uuid_from_aslam_id(vertex.mission_id):
            continue
        frames = vertex.n_visual_frame.frames
        assert len(frames) == len(db_cameras), \
            f"Error: Assumed lengths are equal, but got {len(frames)} != {len(db_cameras)}."
        for db_camera, frame in zip(db_cameras, frames):
            assert frame.is_valid, "Assumed that frame is valid, got invalid frame."
            # TODO: conversion looses precision (from nano seconds to micro seconds)!
            time = datetime.fromtimestamp(float(frame.timestamp) / 10 ** 9)
            observation_id = uuid_from_aslam_id(frame.id)
            db_camera_observation = CameraObservation(id=observation_id,
                                                      pose=db_poses[vertex_id], sensor=db_camera, camera=db_camera,
                                                      algorithm="maplab feature extractor",
                                                      algorithm_settings={'descriptor_scales': 20,
                                                                          'keypoint_descriptor_size': 48,
                                                                          'keypoint_measurement_sigmas': 0.8},
                                                      created_at=time, updated_at=time)
            keypoint_num = len(frame.keypoint_measurement_sigmas)
            keypoint_positions = np.array(frame.keypoint_measurements).reshape(keypoint_num, 2)
            keypoint_descriptors = np.frombuffer(frame.keypoint_descriptors, dtype=np.uint8) \
                .reshape(keypoint_num, frame.keypoint_descriptor_size)
            assert len(keypoint_positions) == len(keypoint_descriptors), \
                "Assumed that number of keypoints is equal to number of descriptors."
            assert len(keypoint_positions) == len(frame.landmark_ids), \
                "Assumed that number of keypoints is equal to number of landmark ids"
            for position, descriptor, lm_id in zip(keypoint_positions, keypoint_descriptors, frame.landmark_ids):
                if uuid_from_aslam_id(lm_id) in db_landmarks.keys():
                    # Note keypoints with invalid landmark id are discarded automatically
                    db_camera_keypoints.append(CameraKeypoint(point=f"POINT({position[0]} {position[1]})",
                                                              descriptor=json.dumps(descriptor.tolist()),
                                                              observation=db_camera_observation,
                                                              landmark=db_landmarks[uuid_from_aslam_id(lm_id)]))
    print("Commit camera keypoints to database.")
    session.add_all(db_camera_keypoints)
    session.commit()

    # collect (between) edges of the mission
    db_edges = []
    edges = vimap.edges()
    print("Loading edges: ")
    for vertex_id, vertex in vertices.items():
        if mission_id != uuid_from_aslam_id(vertex.mission_id):
            continue
        frames = vertex.n_visual_frame.frames
        assert len(frames) == len(db_cameras), \
            f"Error: Assumed lengths are equal, but got {len(frames)} != {len(db_cameras)}."
        # collect edges for last frame, since observation ids are per frame basis,
        # but we only have one edge id between poses in the maplab vi-map
        outgoing_edge_ids = [uuid_from_aslam_id(edge_id) for edge_id in vertex.outgoing]
        for edge_id in outgoing_edge_ids:
            edge_dict = MessageToDict(edges[edge_id])
            edge_type = get_edge_type(edge_dict)
            vertex_from_id = uuid_from_aslam_id(ParseDict(edge_dict[edge_type].pop('from'),
                                                          vi_map_pb2.aslam_dot_common_dot_id__pb2.Id()))
            vertex_to_id = uuid_from_aslam_id(ParseDict(edge_dict[edge_type].pop('to'),
                                                    vi_map_pb2.aslam_dot_common_dot_id__pb2.Id()))
            assert vertex_from_id == vertex_id, "Assumed that vertex_from_id of outgoing edge is vertex_id"
            from_observation_id = uuid_from_aslam_id(vertex.n_visual_frame.frames[-1].id)
            to_observation_id = uuid_from_aslam_id(vertices[vertex_to_id].n_visual_frame.frames[-1].id)
            db_edges += [BetweenEdge(id=edge_id, edge_info=edge_dict,
                                     from_observation_id=from_observation_id, to_observation_id=to_observation_id)]
    print("Commit edges to database.")
    session.add_all(db_edges)
    session.commit()


def to_file(session, output_dir, map_name):
    map_query = session.query(Map).filter(Map.name == map_name)
    if len(map_query.all()) == 0:
        print(f"Map named '{map_name}' not found!")
        return
    assert len(map_query.all()) == 1, f"There must be exactly one map of name {map_name}."
    db_map = map_query[0]
    # TODO: for now only one mission supported
    db_posegraph = db_map.posegraphs[0]

    vimap = VIMap()

    print("Load sensors ond mission information")
    db_sensor_rig = db_posegraph.sensor_rig
    assert len(db_sensor_rig) == 1, "There must be exactly one sensor rig per posegraph"
    db_sensor_rig = db_sensor_rig[0]
    sensors_config = db_sensor_rig.description['config']
    # store sensors
    vimap.sensors = json.loads(sensors_config)

    # start with standard base frame
    mission_base_frame = vi_map_pb2.MissionBaseframe()
    # TODO: now, only the identity transform is supported
    mission_base_frame.T_G_M.extend([0, 0, 0, 1, 0, 0, 0])
    mission_base_frame.T_G_M_covariance.extend(np.eye(6).flatten())
    mission_base_frames = {uuid4(): mission_base_frame}
    # store mission_base_frames
    for mbf_id, mbf in mission_base_frames.items():
        vimap.message.mission_base_frame_ids.extend([aslam_id_from_uuid(mbf_id)])
        vimap.message.mission_base_frames.extend([mbf])
    # add mission settings
    mission = vi_map_pb2.Mission()
    # Note: sensor_rig id equal ncamera id
    db_cameras = session.query(Camera).filter(Camera.sensor_rig_id == db_sensor_rig.id).all()
    db_cameras_ordered = []
    for camera in db_cameras:
        db_cameras_ordered.append(camera)
    num_cameras = len(db_cameras_ordered)
    print(f"Found {num_cameras}-camera")
    mission.ncamera_id.CopyFrom(aslam_id_from_uuid(db_sensor_rig.id))
    # get imu
    db_imus = session.query(IMU).join(SensorRig).filter(SensorRig.id == db_sensor_rig.id).all()
    assert len(db_imus) <= 1, "Assumed at most one imu."
    if len(db_imus) == 1:
        print("Found IMU!")
        mission.imu_id.CopyFrom(aslam_id_from_uuid(db_imus[0].id))
    # store missions
    mission.baseframe_id.CopyFrom(vimap.message.mission_base_frame_ids[0])
    mission_id = db_posegraph.id
    missions = {mission_id: mission}
    for m_id, m in missions.items():
        vimap.message.mission_ids.extend([aslam_id_from_uuid(m_id)])
        vimap.message.missions.extend([m])

    def keypoints_data_from_subquery(keypoints_query):
        db_data = session.execute(select([func.ST_x(keypoints_query.columns.point),
                                          func.ST_y(keypoints_query.columns.point),
                                          keypoints_query.columns.descriptor,
                                          keypoints_query.columns.landmark_id]).select_from(keypoints_query)).all()
        measurements = []
        descriptors = bytes()
        landmark_ids = []
        for row in db_data:
            measurements += [row[0], row[1]]
            descriptors += np.array(json.loads(row[2]), dtype=np.uint8).tobytes()
            landmark_ids += [aslam_id_from_uuid(row[3])]
        return {'num_keypoints': len(db_data), 'measurements': measurements, 'descriptors': descriptors,
                'landmark_ids': landmark_ids}

    def global_positioned_landmarks_from_subquery(landmark_query):
        db_data = session.execute(select([landmark_query.columns.id,
                                          func.ST_x(landmark_query.columns.position),
                                          func.ST_y(landmark_query.columns.position),
                                          func.ST_z(landmark_query.columns.position),
                                          landmark_query.columns.uncertainty,
                                          landmark_query.columns.descriptor]).select_from(landmark_query)).all()
        landmarks = {}
        for row in db_data:
            landmark = vi_map_pb2.Landmark()
            landmark.id.CopyFrom(aslam_id_from_uuid(row[0]))
            landmark.position.extend(row[1:4])
            landmark.quality = row[5]['quality']
            landmarks[row[0]] = landmark
        return landmarks

    print("Query landmarks")
    landmarks_query = session.query(Landmark).join(CameraKeypoint).join(Observation) \
        .join(Camera).join(SensorRig).filter(SensorRig.id == db_sensor_rig.id).subquery()
    landmarks = global_positioned_landmarks_from_subquery(landmarks_query)

    # collect vertices
    print("Process vertices")
    vertices = {}
    db_poses = db_posegraph.poses
    for db_pose in tqdm(db_poses, total=len(db_poses)):
        vertex_id = db_pose.id
        vertex = vi_map_pb2.ViwlsVertex()
        # add mission id
        vertex.mission_id.CopyFrom(aslam_id_from_uuid(mission_id))
        # add T_M_I
        position_stmt = select([func.ST_X(db_pose.position), func.ST_Y(db_pose.position), func.ST_Z(db_pose.position),
                                func.ST_X(db_pose.rotation_vector), func.ST_Y(db_pose.rotation_vector),
                                func.ST_Z(db_pose.rotation_vector)])
        position_and_rotation_vector = session.execute(position_stmt).one()
        position = position_and_rotation_vector[0:3]
        quaternion = Rotation.from_rotvec(position_and_rotation_vector[3:7]).as_quat()
        vertex.T_M_I.extend(np.append(quaternion, position))
        # add n_visual_frame
        n_visual_frame = vi_map_pb2.aslam__serialization_dot_visual__frame__pb2.VisualNFrame()
        n_visual_frame.id.CopyFrom(aslam_id_from_uuid(uuid4()))
        # collect frames of nframe with camera order
        assert len(db_pose.observations) == num_cameras, \
            print(f"Assumed that there are exactly {num_cameras} observations, but got {len(db_pose.observations)}.")
        frames = {}
        for observation in db_pose.observations:
            assert observation.type == ObservationType.Camera, \
                f"Assumed that the pose has only camera observations, but got observation type {observation.type}."
            frame = vi_map_pb2.aslam__serialization_dot_visual__frame__pb2.VisualFrame()
            frame.is_valid = True
            frame.timestamp = int(observation.updated_at.timestamp() * 10 ** 9)
            # collect camera keypoints
            keypoints = session.query(CameraKeypoint).join(CameraObservation) \
                .filter(Observation.id == observation.id).subquery()
            keypoints_data = keypoints_data_from_subquery(keypoints)
            num_keypoints = keypoints_data['num_keypoints']
            if num_keypoints > 0:
                frame.descriptor_scales.extend([observation.algorithm_settings['descriptor_scales']] * num_keypoints)
                frame.keypoint_descriptor_size = observation.algorithm_settings['keypoint_descriptor_size']
                frame.keypoint_descriptors = keypoints_data['descriptors']
                frame.keypoint_measurement_sigmas.extend(
                    [observation.algorithm_settings['keypoint_measurement_sigmas']] * num_keypoints)
                frame.keypoint_measurements.extend(keypoints_data['measurements'])
                frame.landmark_ids.extend(keypoints_data['landmark_ids'])
                frame.tag_ids.extend([-1] * num_keypoints)
                frame.track_ids.extend([-1] * num_keypoints)
            frame.id.CopyFrom(aslam_id_from_uuid(observation.id))
            frames[observation.sensor_id] = frame
        frames_ordered = []
        for camera in db_cameras_ordered:
            frames_ordered.append(frames[camera.id])
        # add frame_indices, keypoint_indices to landmarks
        for frame_index, frame in enumerate(frames_ordered):
            for keypoint_index, landmark_id in enumerate(frame.landmark_ids):
                landmark = landmarks[uuid_from_aslam_id(landmark_id)]
                landmark.frame_indices.extend([frame_index])
                landmark.keypoint_indices.extend([keypoint_index])
                landmark.vertex_ids.extend([aslam_id_from_uuid(vertex_id)])
        n_visual_frame.frames.extend(frames_ordered)
        vertex.n_visual_frame.CopyFrom(n_visual_frame)
        # add landmark store
        landmark_store = vi_map_pb2.LandmarkStore()
        vertex.landmark_store.CopyFrom(landmark_store)
        # add velocity
        vertex.v_M.extend([0, 0, 0])
        # add biases
        vertex.accel_bias.extend([0, 0, 0])
        vertex.gyro_bias.extend([0, 0, 0])
        vertices[vertex_id] = vertex

    print("Process landmarks")
    for landmark_id, landmark in landmarks.items():
        num_keypoints = len(landmark.frame_indices)
        if num_keypoints == 0:
            continue
        first_vertex_id = landmark.vertex_ids[0]
        lowest_timestamp = vertices[uuid_from_aslam_id(first_vertex_id)].n_visual_frame.frames[0].timestamp
        for vertex_id in landmark.vertex_ids:
            for frame in vertices[uuid_from_aslam_id(vertex_id)].n_visual_frame.frames:
                timestamp = frame.timestamp
                if timestamp < lowest_timestamp:
                    lowest_timestamp = timestamp
                    first_vertex_id = vertex_id
        landmark_vertex_ref = vi_map_pb2.LandmarkToVertexReference()
        landmark_vertex_ref.vertex_id.CopyFrom(first_vertex_id)
        landmark_vertex_ref.landmark_id.CopyFrom(aslam_id_from_uuid(landmark_id))
        vimap.message.landmark_index.extend([landmark_vertex_ref])
        # rotate the landmark into the right position
        vertex = vertices[uuid_from_aslam_id(first_vertex_id)]
        vertex_transform = np.array(vertex.T_M_I)
        vertex_quaternion = vertex_transform[0:4]
        vertex_position = vertex_transform[4:7]
        global_pos = np.array(landmark.position)
        local_pos = Rotation.from_quat(vertex_quaternion).inv().apply(global_pos - vertex_position)
        landmark.position[0:3] = local_pos
        # store landmarks
        vertex.landmark_store.landmarks.extend([landmark])

    print("Process edges")
    edges = {}
    # initialize edges and set edge.vertex_from_id
    for db_pose in db_poses:
        db_edges = session.query(BetweenEdge).join(Observation, Observation.id == BetweenEdge.from_observation_id) \
            .join(Pose).filter(Pose.id == db_pose.id).all()
        for db_edge in db_edges:
            edge_dict = db_edge.edge_info
            edge_type = get_edge_type(edge_dict)
            edge = ParseDict(db_edge.edge_info, vi_map_pb2.Edge())
            edge.__getattribute__(edge_type).__getattribute__("from").CopyFrom(aslam_id_from_uuid(db_pose.id))
            edges[db_edge.id] = edge
    # collect vertices with no incoming edge and set edge.vertex_to_id
    starting_vertex_ids = []
    for db_pose in db_poses:
        db_edges = session.query(BetweenEdge).join(Observation, Observation.id == BetweenEdge.to_observation_id) \
            .join(Pose).filter(Pose.id == db_pose.id).all()
        if len(db_edges) == 0:
            starting_vertex_ids += [aslam_id_from_uuid(db_pose.id)]
        for db_edge in db_edges:
            edge = edges[db_edge.id]
            edge_dict = db_edge.edge_info
            edge_type = get_edge_type(edge_dict)
            edge.__getattribute__(edge_type).__getattribute__("to").CopyFrom(aslam_id_from_uuid(db_pose.id))

    if len(starting_vertex_ids) == 0:
        print(f"Found no root vertex id!")
    if len(starting_vertex_ids) == 1:
        root_vertex_id = starting_vertex_ids[0]
        print(f"Found root vertex id: {uuid_from_aslam_id(root_vertex_id)}")
    else:
        print(f"Found {len(starting_vertex_ids)} vertices with no incoming edge.")

    # store root vertex
    assert len(starting_vertex_ids) == 1, "Assumed there is exactly one root vertex."
    vimap.message.missions[0].root_vertex_id.CopyFrom(root_vertex_id)

    # store edges
    for edge_id, edge in edges.items():
        vimap.message.edges.extend([edge])
        vimap.message.edge_ids.extend([aslam_id_from_uuid(edge_id)])

    # store vertices
    for vertex_id, vertex in vertices.items():
        vimap.message.vertex_ids.extend([aslam_id_from_uuid(vertex_id)])
        vimap.message.vertices.extend([vertex])

    print("Export to vimap")
    vimap.save_to(output_dir, compressed=True)

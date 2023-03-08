import msgpack
from model import *
from datetime import datetime
from pathlib import Path
import openschema_utils as utils
from geoalchemy2 import func
from tqdm import tqdm
from sqlalchemy import table, column, select, join, func
from sqlalchemy.dialects import postgresql

def to_db(session, input_file, map_name):
    with open(input_file, "rb") as data_file:
        loaded_data = msgpack.unpackb(
            data_file.read(), use_list=True, raw=False)

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
        newmap = Map(name=map_name,
                     description={"T_global": [0.0]*12},
                     created_at=ts, updated_at=ts)

        pg = PoseGraph(name="SLAM graph", map=newmap,
                       description={"Some_generic_setting": 0.2})
        sensor_rig.posegraph = pg

        landmarks = {}
        # Add landmarks
        for landmark_id in tqdm(list(loaded_data["landmarks"].keys()), desc="Landmarks"):
            landmark_msgpack = loaded_data["landmarks"][landmark_id]
            landmark_pos_w = landmark_msgpack["pos_w"]

            landmarks[int(landmark_id)] = Landmark(
                position=f"POINTZ({landmark_pos_w[0]} {landmark_pos_w[1]} {landmark_pos_w[2]})")

        poses = []
        observations = {}
        camera_keypoints = []
        # Add keypoints
        # go over all keyframes
        for keyframe_id in tqdm(list(loaded_data["keyframes"].keys()), desc="Observations"):
            keyframe_msgpack = loaded_data["keyframes"][keyframe_id]
            keypts_msgpack = keyframe_msgpack["keypts"]
            lm_ids_msgpack = keyframe_msgpack["lm_ids"]
            descriptors_msgpack = keyframe_msgpack["descs"]
            depths_msgpack = keyframe_msgpack["depths"]
            depth_thr_msgpack = keyframe_msgpack["depth_thr"]
            n_scale_levels_msgpack = keyframe_msgpack["n_scale_levels"]
            scale_factor_msgpack = keyframe_msgpack["scale_factor"]
            x_rights_msgpack = keyframe_msgpack["x_rights"]
            undists_msgpack = keyframe_msgpack["undists"]

            trans_cw = keyframe_msgpack["trans_cw"]
            # TODO: Calculate unit vector from quaternion and add to pose
            euler = utils.quaternion_to_euler(*keyframe_msgpack["rot_cw"])
            pose = Pose(
                position=f"POINTZ({trans_cw[0]} {trans_cw[1]} {trans_cw[2]})",
                # TODO: normal vector or euler?
                normal=f"POINTZ({euler[0]} {euler[1]} {euler[2]})",
                posegraph=pg)
            poses.append(pose)

            creation_time = datetime.fromtimestamp(
                float(keyframe_msgpack["ts"])/1000.0)
            camera_observation = CameraObservation(
                pose=pose, sensor=camera, camera=camera, algorithm="openVSLAM",
                created_at=creation_time,
                updated_at=creation_time,
                algorithm_settings={'openVSLAM':
                                    {'depth_thr': depth_thr_msgpack,
                                     'n_scale_levels': n_scale_levels_msgpack,
                                     'scale_factor': scale_factor_msgpack}
                                    })
            observations[int(keyframe_id)] = camera_observation

            for keypt, lm_id, descriptor, depth, x_right, undist in zip(keypts_msgpack, lm_ids_msgpack, descriptors_msgpack, depths_msgpack, x_rights_msgpack, undists_msgpack):
                ckp = CameraKeypoint(point=f"POINT({keypt['pt'][0]} {keypt['pt'][1]})",
                                     descriptor={'openVSLAM':
                                                 {'ORB': descriptor,
                                                  'depth': depth,
                                                  'x_right': x_right,
                                                  'ang': keypt['ang'],
                                                  'oct': keypt['oct'],
                                                  'undist': undist}
                                                 },
                                     observation=camera_observation)
                if lm_id != -1 and int(lm_id) in landmarks.keys():
                    ckp.landmark = landmarks[int(lm_id)]
                camera_keypoints.append(ckp)

        session.add_all([newmap, pg, sensor_rig, camera] +
                        list(landmarks.values()) +
                        camera_keypoints + poses + list(observations.values()))
        session.commit()

        # TODO: adding CameraObservation as Observation is not possible direct -> need to add id manually -> need to commit first to get an ID
        # Maybe there is a more elgant way to use the automatic deduction of dependencies with inheritence / upcast? E.g., observation_id = Observation(current_observation).
        edges = []
        # Add (covisibility and loop) edges
        for keyframe_id in tqdm(list(loaded_data["keyframes"].keys()), desc="Edges"):
            keyframe_msgpack = loaded_data["keyframes"][keyframe_id]
            current_observation = observations[int(keyframe_id)]
            for child_keyframe_id in keyframe_msgpack['span_children']:
                child_observation = observations[child_keyframe_id]
                edges.append(BetweenEdge(
                    from_observation_id=current_observation.id, to_observation_id=child_observation.id))

            for loop_edge_id in keyframe_msgpack['loop_edges']:
                child_observation = observations[loop_edge_id]
                edges.append(BetweenEdge(from_observation_id=current_observation.id,
                                         to_observation_id=child_observation.id, edge_info={"is_loop_edge": True}))

        session.add_all(edges)
        session.commit()


def to_file(session, output_file, map_name):
    msg_pack_file_path = Path(output_file)

    all_sensors = session.query(Sensor).join(SensorRig).join(
        PoseGraph).join(Map).filter(Map.name == map_name).all()

    all_observations = session.query(Observation).join(Pose).join(
        PoseGraph).join(Map).filter(Map.name == map_name).all()
    # UUID -> IDX mapping
    observation_uuid_idx_map = {}
    for idx, observation in enumerate(all_observations):
        observation_uuid_idx_map[observation.id] = idx

    all_landmarks = session.query(Landmark).join(CameraKeypoint).join(Observation, CameraKeypoint.observation_id ==
                                                                    Observation.id).join(Pose).join(PoseGraph).join(Map).filter(Map.name == map_name).all()
    # UUID -> IDX mapping
    landmark_uuid_idx_map = {}
    for idx, landmark in enumerate(all_landmarks):
        landmark_uuid_idx_map[landmark.id] = idx

    with open(msg_pack_file_path, "wb") as output_file:
        data = {}
        for sensor in all_sensors:
            cameras = {sensor.name: sensor.description['openVSLAM_config']}
            data['cameras'] = cameras

        # TODO: frame_next_id needs to be checked?
        data['frame_next_id'] = data['keyframe_next_id'] = len(all_observations)
        data['landmark_next_id'] = len(all_landmarks)

        # TODO: why does this not work with alchemy query? -> dialect postgres needed for "DISTINCT ON" -> issue?
        # sub_query = select([Landmark, func.count().label("n_vis")]).select_from(Landmark).join(CameraKeypoint).group_by(Landmark.id).subquery()
        # optimized_landmark_query = select([sub_query.c.id.label("lm_id"), 
        #                 sub_query.c.n_vis.label("n_vis"), 
        #                 CameraKeypoint.id.label("ckp_id"), 
        #                 CameraObservation.id.label("cobs_id"),
        #                 func.ST_X(sub_query.c.position).label("pos_x"),
        #                 func.ST_Y(sub_query.c.position).label("pos_y"),
        #                 func.ST_Z(sub_query.c.position).label("pos_z")]).distinct(sub_query.c.id).select_from(sub_query).join(CameraKeypoint).join(CameraObservation).join(Pose).join(PoseGraph).join(Map).filter(Map.name == map_name).compile(dialect=postgresql.dialect())
        # print(str(optimized_landmark_query))

        # TODO: Do this with SQLAlchemy to avoid string matching!
        optimized_landmark_query = "SELECT DISTINCT ON (landmarks_with_count.id) " \
            "landmarks_with_count.id AS lm_id, " \
            "landmarks_with_count.n_vis AS n_vis, " \
            "camera_keypoint.id AS ckp_id, " \
            "camera_observation.id AS cobs_id, " \
            "ST_X(landmarks_with_count.position) AS pos_x, " \
            "ST_Y(landmarks_with_count.position) AS pos_y, " \
            "ST_Z(landmarks_with_count.position) AS pos_z " \
            "FROM ( " \
            "    SELECT landmark.*, COUNT(*) AS n_vis " \
            "        FROM landmark " \
            "            JOIN keypoint ON keypoint.landmark_id = landmark.id " \
            "            RIGHT JOIN camera_keypoint ON camera_keypoint.id = keypoint.id " \
            "        GROUP BY landmark.id " \
            ") AS landmarks_with_count  " \
            "    JOIN keypoint ON keypoint.landmark_id = landmarks_with_count.id " \
            "    RIGHT JOIN camera_keypoint ON camera_keypoint.id = keypoint.id " \
            "    JOIN camera_observation ON camera_observation.id = keypoint.observation_id" \
            "    JOIN observation ON observation.id = camera_observation.id " \
            "    JOIN pose ON pose.id = observation.pose_id " \
            "    JOIN posegraph ON posegraph.id = pose.posegraph_id " \
            "    JOIN map ON map.id = posegraph.map_id " \
            f"   WHERE map.name = '{map_name}' "

        landmarks = {}
        for special_landmark_query in tqdm(session.execute(optimized_landmark_query).all()):
            lm_idx = landmark_uuid_idx_map[special_landmark_query.lm_id]
            landmarks[lm_idx] = {'1st_keyfrm': special_landmark_query.cobs_id,
                                'n_fnd': special_landmark_query.n_vis,
                                'n_vis': special_landmark_query.n_vis,
                                'pos_w': [special_landmark_query.pos_x, special_landmark_query.pos_y, special_landmark_query.pos_z]
                                }

        keyframes = {}
        for observation in tqdm(all_observations, desc="Observations"):
            kf_idx = observation_uuid_idx_map[observation.id]
            depths = []
            x_rights = []
            keypoints = []
            descs = []
            lm_ids = []
            undist = []

            for keypoint in observation.keypoints:
                depths.append(keypoint.descriptor['openVSLAM']['depth'])
                x_rights.append(keypoint.descriptor['openVSLAM']['x_right'])
                keypoints.append({'ang': keypoint.descriptor['openVSLAM']['ang'],
                                'oct': keypoint.descriptor['openVSLAM']['oct'],
                                'pt': [session.execute(func.ST_X(keypoint.point)).scalar(),
                                        session.execute(func.ST_Y(keypoint.point)).scalar()]})
                descs.append(keypoint.descriptor['openVSLAM']['ORB'])
                lm_ids.append(landmark_uuid_idx_map[keypoint.landmark.id]
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
                                'rot_cw': utils.euler_to_quaternion(
                                    roll=session.execute(
                                        func.ST_X(observation.pose.rotation_vector)).scalar(),
                                    pitch=session.execute(
                                        func.ST_Y(observation.pose.rotation_vector)).scalar(),
                                    yaw=session.execute(func.ST_Z(observation.pose.rotation_vector)).scalar()),
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

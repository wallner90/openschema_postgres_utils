from math import sin, cos, pi
from pathlib import Path
from datetime import datetime

import json

from pyclothoids import Clothoid
from scipy.spatial.transform import Rotation


from model import *

json_file_path = Path(
    "lane_map.json")


def to_db(session, input_file, map_name):
    with open(input_file, "rb") as data_file:
        l = json.load(data_file)
        x = json.dumps(l, ensure_ascii=True)
        loaded_data = json.loads(x)

        ts = datetime.utcnow()
        new_map = Map(name=map_name,
                      description={"T_global": [0.0]*12},
                      created_at=ts, updated_at=ts)

        pg = PoseGraph(name="Virtual lane pose graph", map=new_map,
                       description={"Some_generic_setting": 0.2})

        # all (virtual) keypoints share the same (virtual) pose for semantic_observation
        pose = Pose(position=f"POINTZ({0} {0} {0})", posegraph=pg)

        semantic_observation = SemanticObservation(
            pose=pose, algorithm="lane_map", created_at=ts, updated_at=ts,
            algorithm_settings={"lane_map":
                                {"test": 123,
                                 }})

        #
        id = 0
        keypoints = []
        many_to_many_associations = []
        semantic_lanes = {}
        landmarks = []
        semantic_lines = {}
        semantic_geometry = {}
        lanes = list(loaded_data["laneList"])
        goals = list(loaded_data["goalList"])
        stations = list(loaded_data["stationList"])
        lanes_and_semantic_lanes = {}
        semantic_lines_info = {}
        semantic_line_id = 0
        for lane in list(lanes):
            semantic_line1 = SemanticLineString()
            semantic_line2 = SemanticLineString()
           
            print("lane is ", lane)
            goal_id_1 = lane["startNodeId"] - 1  # goal 1 is start Node!
            goal1 = goals[goal_id_1]
            goal_pos1 = goal1["pose"]
            pos_x_1 = goal_pos1["x"]
            pos_y_1 = goal_pos1["y"]
            pos_yaw_1 = goal_pos1["yaw"]
            relatedStations = []
            for stationId in goal1["stationId"]:
                for station in stations:
                    if station["id"] == stationId:
                        relatedStations.append(station)
            
            pose_rotvec_1 = Rotation.from_euler('zyx', [sin(pos_yaw_1 * (180 / pi)) * cos(0), 0.0, cos(pos_yaw_1 * (180 / pi)) * cos(0)]).as_rotvec()
            lm_1 = Landmark(position=f'POINTZ({pos_x_1} {pos_y_1} {0})',
                                            rotation_vector=f'POINTZ({pose_rotvec_1[0]} {pose_rotvec_1[1]} {pose_rotvec_1[2]})',
                                            descriptor={"stations": relatedStations, "goalId": goal_id_1,
                                                        "goalProperty": goal1["goalProperty"]})
            landmarks.append(lm_1)
            keypoints.append(SemanticKeypoint(
                observation=semantic_observation, landmark=lm_1))
            m2m_assoc1 = ManyLandmarkHasManySemanticGeometry(order_idx=0, landmark=lm_1)
            m2m_assoc2 = ManyLandmarkHasManySemanticGeometry(order_idx=0, landmark=lm_1)
            semantic_line1.landmarks.append(m2m_assoc1)
            semantic_line2.landmarks.append(m2m_assoc2)
            many_to_many_associations.append(m2m_assoc1)
            many_to_many_associations.append(m2m_assoc2)

            goal_id_2 = lane["endNodeId"] - 1  # goal 2 is end Node!
            goal2 = goals[goal_id_2]
            goal_pos2 = goal2["pose"]
            pos_x_2 = goal_pos2["x"]
            pos_y_2 = goal_pos2["y"]
            pos_yaw_2 = goal_pos2["yaw"]
            print(pos_x_2, pos_y_2, pos_yaw_2)
            relatedStations = []

            # sample virtual landmarks inbetween to generate clothoid
            clothoid = Clothoid.G1Hermite(x0=pos_x_1, y0=pos_y_1, t0=pos_yaw_1, x1=pos_x_2, y1=pos_x_2, t1=pos_yaw_2)
            samples_x, samples_y = clothoid.SampleXY(50)
            idx = 1
            for sample_x,sample_y in zip(samples_x, samples_y):
                lm = Landmark(position=f'POINTZ({sample_x} {sample_y} {0})',
                                descriptor={"sampled_clothoid": True})
                landmarks.append(lm)
                keypoints.append(SemanticKeypoint(
                                observation=semantic_observation, landmark=lm))
                m2m_assoc1 = ManyLandmarkHasManySemanticGeometry(order_idx=idx, landmark=lm)
                m2m_assoc2 = ManyLandmarkHasManySemanticGeometry(order_idx=idx, landmark=lm)
                semantic_line1.landmarks.append(m2m_assoc1)
                semantic_line2.landmarks.append(m2m_assoc2)
                many_to_many_associations.append(m2m_assoc1)
                many_to_many_associations.append(m2m_assoc2)
                idx = idx + 1

            for stationId in goal2["stationId"]:
                for station in stations:
                    if station["id"] == stationId:
                        relatedStations.append(station)

            pose_rotvec_2 = Rotation.from_euler("zyx", [sin(pos_yaw_2 * (180 / pi)) * cos(0), 0.0, cos(pos_yaw_2 * (180 / pi)) * cos(0)]).as_rotvec()
            lm_2 = Landmark(position=f'POINTZ({pos_x_2} {pos_y_2} {0})',
                                            rotation_vector=f'POINTZ({pose_rotvec_2[0]} {pose_rotvec_2[1]} {pose_rotvec_2[2]})',
                                            descriptor={"stations": relatedStations, "goalId": goal_id_2,
                                                        "goalProperty": goal2["goalProperty"]})
            landmarks.append(lm_2)     
            keypoints.append(SemanticKeypoint(
                observation=semantic_observation, landmark=lm_2))
            m2m_assoc1 = ManyLandmarkHasManySemanticGeometry(order_idx=idx, landmark=lm_2)
            m2m_assoc2 = ManyLandmarkHasManySemanticGeometry(order_idx=idx, landmark=lm_2)
            semantic_line1.landmarks.append(m2m_assoc1)
            semantic_line2.landmarks.append(m2m_assoc2)
            many_to_many_associations.append(m2m_assoc1)
            many_to_many_associations.append(m2m_assoc2)

            # line String IS a geometry Objectu
            # semantic_line1.landmarks.append(landmarks)
            # semantic_line1.landmarks.extend(landmarks)
            # semantic_line2.landmarks.append(landmarks)
            # semantic_line2.landmarks.extend(landmarks)
            forwardDriving = lane["virtualLane"]["forwardDirection"]["driveForwardOriented"]
            forwardBackwardDriving = lane["virtualLane"]["forwardDirection"]["driveBackwardOriented"]
            backwardDriving = lane["virtualLane"]["backwardDirection"]["driveForwardOriented"]
            backwardBackwardDriving = lane["virtualLane"]["backwardDirection"]["driveBackwardOriented"]

            lanes_and_semantic_lanes[id] = [forwardDriving, backwardDriving, forwardBackwardDriving,
                                            backwardBackwardDriving]
            semantic_lanes[id] = SemanticLane(name="lane_" + str(lane["id"]))
            semantic_lines_info[id] = [semantic_line_id, semantic_line_id + 1]
            semantic_lines[semantic_line_id] = semantic_line1
            semantic_line_id += 1
            semantic_lines[semantic_line_id] = semantic_line2
            semantic_line_id += 1
            id += 1

        session.add_all([semantic_observation, pg, new_map] +
                        keypoints + 
                        many_to_many_associations +
                        landmarks +
                        list(semantic_lines.values()) +
                        list(semantic_geometry.values()))
        session.commit()

        for id, semantic_lane in semantic_lanes.items():
            forwardDrivingInfo, backwardDrivingInfo, forwardBackwardDrivingInfo, backwardBackwardDrivingInfo = \
                lanes_and_semantic_lanes[id]
            print("right! ", forwardDrivingInfo, backwardDrivingInfo, forwardBackwardDrivingInfo,
                  backwardBackwardDrivingInfo, id, semantic_lane.name)
            laneInfo = ""
            drivingDirection = ""
            if forwardDrivingInfo:
                semantic_lane.right_line_id = semantic_lines[semantic_lines_info[id][0]].id
                semantic_lane.left_line_id = semantic_lines[semantic_lines_info[id][1]].id
                laneInfo = "two_way" if backwardDrivingInfo or backwardBackwardDrivingInfo else "one_way"
                drivingDirection = "forward_and_backward" if forwardBackwardDrivingInfo or backwardBackwardDrivingInfo else "forward"
            elif backwardDrivingInfo:
                semantic_lane.right_line_id = semantic_lines[semantic_lines_info[id][1]].id
                semantic_lane.left_line_id = semantic_lines[semantic_lines_info[id][0]].id
                laneInfo = "two_way" if forwardBackwardDrivingInfo else "one_way"
                drivingDirection = "forward_and_backward" if backwardBackwardDrivingInfo or forwardBackwardDrivingInfo else "forward"
            elif forwardBackwardDrivingInfo:
                semantic_lane.right_line_id = semantic_lines[semantic_lines_info[id][0]].id
                semantic_lane.left_line_id = semantic_lines[semantic_lines_info[id][1]].id
                laneInfo = "two_way" if backwardBackwardDrivingInfo else "one_way"
                drivingDirection = "backward"
            elif backwardBackwardDrivingInfo:
                semantic_lane.right_line_id = semantic_lines[semantic_lines_info[id][1]].id
                semantic_lane.left_line_id = semantic_lines[semantic_lines_info[id][0]].id
                laneInfo = "one_way"
                drivingDirection = "backward"
            semantic_lane.description = {
                "laneInfo": laneInfo, "drivingDirection": drivingDirection}

        session.add_all(list(semantic_lanes.values()))
        session.commit()

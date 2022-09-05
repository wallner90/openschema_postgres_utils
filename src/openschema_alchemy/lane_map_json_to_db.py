from math import sin, cos
from pathlib import Path

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.ddl import CreateSchema

from model import *

json_file_path = Path(
    "lane_map.json")
pi = 22/7
with open(json_file_path, "rb") as data_file:
    loaded_data = json.load(data_file)

    engine = create_engine(
        'postgresql://postgres:postgres@127.0.0.1:5432/postgres_alchemy_ait', echo=False)
    if not engine.dialect.has_schema(engine, 'public'):
        engine.execute(CreateSchema('public'))
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    #
    id = 0
    semantic_lanes = {}
    landmarks = {}
    semantic_lines = {}
    semantic_geometry = {}
    lanes = list(loaded_data["laneList"])
    goals = list(loaded_data["goalList"])
    stations = list(loaded_data["stationList"])
    lanes_and_semantic_lanes = {}
    semantic_lines_info = {}
    semantic_line_id = 0
    for lane in list(lanes):
        print(lane)
        goal_id_1 = lane["startNodeId"] - 1 # goal 1 is start Node!
        goal1 = goals[goal_id_1]
        goal_pos1 = goal1["pose"]
        pos_x = goal_pos1["x"]
        pos_y = goal_pos1["y"]
        pos_yaw = goal_pos1["yaw"]
        relatedStations = []
        for stationId in goal1["stationId"]:
            for station in stations:
                if station["id"] == stationId:
                    relatedStations.append(station)

        landmarks[goal_id_1] = Landmark(position=f'POINTZ({pos_x} {pos_y} {0})',
                                        normal=f'POINTZ({sin(pos_yaw*(180/pi)) * cos(0)} {0} {cos(pos_yaw*(180/pi)) * cos(0)})',
                                        descriptor={"stations": relatedStations, "goalId": goal_id_1, "goalProperty": goal1["goalProperty"]})
        goal_id_2 = lane["endNodeId"] - 1  # goal 2 is end Node!
        goal2 = goals[goal_id_2]
        goal_pos2 = goal2["pose"]
        pos_x = goal_pos2["x"]
        pos_y = goal_pos2["y"]
        pos_yaw = goal_pos2["yaw"]
        print(pos_x, pos_y, pos_yaw)
        relatedStations = []
        for stationId in goal2["stationId"]:
            for station in stations:
                if station["id"] == stationId:
                    relatedStations.append(station)

        landmarks[goal_id_2] = Landmark(position=f'POINTZ({pos_x} {pos_y} {0})',
                                        normal=f'POINTZ({sin(pos_yaw*(180/pi)) * cos(0)} {0} {cos(pos_yaw*(180/pi)) * cos(0)})',
                                        descriptor={"stations": relatedStations, "goalId": goal_id_2, "goalProperty": goal2["goalProperty"]})
        semantic_line1 = SemanticLineString(type="line_string")  # line String IS a geometry Objectu
        semantic_line1.landmarks.append(landmarks[goal_id_1])
        semantic_line1.landmarks.append(landmarks[goal_id_2])
        semantic_line2 = SemanticLineString(type="line_string")
        semantic_line2.landmarks.append(landmarks[goal_id_1])
        semantic_line2.landmarks.append(landmarks[goal_id_2])
        print("virtual lane ", lane["type"]["virtualLane"])
        forwardDriving = lane["type"]["virtualLane"]["forwardDirection"]["driveForwardOriented"]
        forwardBackwardDriving = lane["type"]["virtualLane"]["forwardDirection"]["driveBackwardOriented"]
        backwardDriving = lane["type"]["virtualLane"]["backwardDirection"]["driveForwardOriented"]
        backwardBackwardDriving = lane["type"]["virtualLane"]["backwardDirection"]["driveBackwardOriented"]

        lanes_and_semantic_lanes[id] = [forwardDriving, backwardDriving, forwardBackwardDriving,
                                        backwardBackwardDriving]
        semantic_lanes[id] = SemanticLane(name="lane_" + str(lane["id"]))
        semantic_lines_info[id] = [semantic_line_id, semantic_line_id + 1]
        semantic_lines[semantic_line_id] = semantic_line1
        semantic_line_id += 1
        semantic_lines[semantic_line_id] = semantic_line2
        semantic_line_id += 1
        id += 1

    session = Session()
    session.add_all(list(landmarks.values()) + list(semantic_lines.values()) + list(semantic_geometry.values()))
    session.commit()

    for id, semantic_lane in semantic_lanes.items():
        forwardDrivingInfo, backwardDrivingInfo, forwardBackwardDrivingInfo, backwardBackwardDrivingInfo = lanes_and_semantic_lanes[id]
        print("right! ", forwardDrivingInfo, backwardDrivingInfo, forwardBackwardDrivingInfo, backwardBackwardDrivingInfo, id, semantic_lane.name)
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
        semantic_lane.description = {"laneInfo": laneInfo, "drivingDirection": drivingDirection}


    session.add_all(list(semantic_lanes.values()))
    session.commit()

from pathlib import Path

import np as np

from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.ddl import CreateSchema

from model import *

yaml_file_path = Path(
    "map.yaml")
pgm_file_path = Path(
    "map.pgm")

with open(yaml_file_path, "rb") as yaml_file, Image.open("/home/manar/Downloads/map.pgm") as pgm_file:
    # For now hard code information because .safe_load has a unfixable python error!
    # loaded_yaml_data = yaml.safe_load(yaml_file)
    # TODO get the offset to match laneMap + gridMap to the same coordinate system!
    origin_point = [-17.8, -6.51, 0]  # loaded_yaml_data["origin"] lower left pixel in the map
    resolution = 0.05  # loaded_yaml_data["resolution"]
    occupied_thresh = 0.65  # loaded_yaml_data["occupied_thresh"]
    free_thresh = 0.25  # loaded_yaml_data["free_thresh"]
    negate = 0  # loaded_yaml_data["negate"]

    pixel_max_x, pixel_max_y = pgm_file.size
    loaded_pgm_data = pgm_file.load()

    engine = create_engine(
        'postgresql://postgres:postgres@127.0.0.1:5432/postgres_alchemy_ait', echo=False)
    if not engine.dialect.has_schema(engine, 'public'):
        engine.execute(CreateSchema('public'))
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    y_coord_max = origin_point[1] + (pixel_max_y*resolution)
    x_coord_max = origin_point[0] + (pixel_max_x*resolution)

    sensor_rig = SensorRig(name="LIDAR  Rig")
    lidar = LIDAR(name="lidar", sensor_rig=sensor_rig)

    landmarks = {}
    id = 0
    for y, y_cord in zip(reversed(range(pixel_max_y)), np.arange(origin_point[1], y_coord_max, resolution)):
        for x, x_cord in zip(range(pixel_max_x), np.arange(origin_point[0], x_coord_max, resolution)):
            pixel_val = loaded_pgm_data[x, y]
            # print(pixel_val, x, y, y_cord, x_cord)
            if negate:
                p = pixel_val / 255.0
            else:
                p = (255 - pixel_val) / 255.0
            if p > occupied_thresh:
                i = 6
                landmarks[id] = Landmark(
                    position=f"POINTZ({x_cord} {y_cord} {0})")
                id += 1
            else:
                i = 5

    # print("len of ", len(landmarks))
    landmarks_size = len(landmarks)

    session = Session()
    session.add_all([sensor_rig, lidar] + list(landmarks.values()))
    session.commit()

    pose = Pose(position=f"POINTZ({0} {0} {0})")
    lidar_observation = LIDARObservation(
        pose=pose, sensor=lidar, lidar=lidar)

    session.add_all([lidar_observation])

    lidar_keypoints = []
    for landmark_id in range(len(landmarks)):
        lkp = LIDARKeypoint(point=f"POINT({0} {0})", lidar_observation=lidar_observation)
        lkp.landmark = landmarks[landmark_id]
        lidar_keypoints.append(lkp)

    session.add_all(lidar_keypoints)

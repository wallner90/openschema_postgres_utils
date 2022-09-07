import numpy as np
import yaml

from pathlib import Path
from PIL import Image
from datetime import datetime

from model import *


def to_db(session, input_file, map_name):
    yaml_file_path = Path(input_file)
    if yaml_file_path.suffix not in [".yaml", ".yml"]:
        print(f"ERROR: Provide *.yaml or *.yml file to load from LiDAR map. Given: {yaml_file_path}")
        return False
    with yaml_file_path.open() as yaml_file:
        loaded_yaml_data = yaml.safe_load(yaml_file)
        pgm_file_name = Path(input_file).parent / loaded_yaml_data["image"]
        with Image.open(pgm_file_name) as pgm_file:
            origin_point =  loaded_yaml_data["origin"]
            resolution = loaded_yaml_data["resolution"]
            occupied_thresh = loaded_yaml_data["occupied_thresh"]
            free_thresh = loaded_yaml_data["free_thresh"]
            negate = loaded_yaml_data["negate"]
            mode = loaded_yaml_data["mode"]

            pixel_max_x, pixel_max_y = pgm_file.size
            loaded_pgm_data = pgm_file.load()

            y_coord_max = origin_point[1] + (pixel_max_y*resolution)
            x_coord_max = origin_point[0] + (pixel_max_x*resolution)

            sensor_rig = SensorRig(name="Virtual LiDAR from map",
                                   description={"T": [0.0]*12})
            lidar = LIDAR(name="lidar", sensor_rig=sensor_rig)
            
            ts = datetime.utcnow()
            new_map = Map(name=map_name,
                     description={"T_global": [0.0]*12},
                     created_at=ts, updated_at=ts)

            pg = PoseGraph(name="Virtual LiDAR graph", map=new_map,
                       description={"Some_generic_setting": 0.2})

            sensor_rig.posegraph = pg

            landmarks = []
            # each landmark needs at least one lidar_keypoint
            keypoints = []
            # all (virtual) keypoints share the same (virtual) lidar_observation
            pose = Pose(position=f"POINTZ({0} {0} {0})", posegraph=pg)
            lidar_observation = LIDARObservation(
                pose=pose, sensor=lidar, lidar=lidar, algorithm="lidar_slam", 
                created_at=ts, updated_at=ts, 
                algorithm_settings={"lidar_slam":
                                        {"mode": mode,
                                         "resolution": resolution,
                                         "negate": negate,
                                         "occupied_thresh": occupied_thresh,
                                         "free_thres": free_thresh
                                         }})
            for y, y_cord in zip(reversed(range(pixel_max_y)), np.arange(origin_point[1], y_coord_max, resolution)):
                for x, x_cord in zip(range(pixel_max_x), np.arange(origin_point[0], x_coord_max, resolution)):
                    pixel_val = loaded_pgm_data[x, y]
                    # print(pixel_val, x, y, y_cord, x_cord)
                    if negate:
                        p = pixel_val / 255.0
                    else:
                        p = (255 - pixel_val) / 255.0
                    if p > occupied_thresh:
                        lm = Landmark(position=f"POINTZ({x_cord} {y_cord} {0})")
                        landmarks.append(lm)
                        keypoints.append(LIDARKeypoint(lidar_observation=lidar_observation, landmark=lm))
                        

            session.add_all([new_map, pg, sensor_rig, lidar, lidar_observation] + landmarks + keypoints)
            session.commit()

import gzip
import os
import yaml
from glob import glob
from google.protobuf import text_format

from maplab.vimap.proto import vi_map_pb2


def merge_vimap_file_to_message(message: vi_map_pb2.VIMap, file_name: str, compressed: bool) -> vi_map_pb2.VIMap:
    with open(file_name, 'rb') as file:
        data = file.read()
    if compressed:
        data = gzip.decompress(data)
    message.MergeFromString(data)


def create_file_type(type_string: str, path=None):
    type_string_to_id = {"missions": 0, "vertices": 1, "edges": 2, "landmark_index": 3}
    if path is None:
        path = type_string
    ft = vi_map_pb2.FileTypeWithPath()
    ft.file_type = type_string_to_id[type_string]
    ft.path = path
    return ft


class VIMap:
    def __init__(self, map_dir: str, compressed: bool = True):
        assert 'vi_map' in os.listdir(map_dir), f"Cannot find 'vi_map' directory in path {map_dir}"
        vimap_dir = map_dir + '/vi_map'

        print("VIMap: loading data")
        self.message = vi_map_pb2.VIMap()
        merge_vimap_file_to_message(self.message, vimap_dir + '/missions', compressed)
        merge_vimap_file_to_message(self.message, vimap_dir + '/landmark_index', compressed)
        for file in glob(vimap_dir + '/edges*') + glob(vimap_dir + '/vertices*'):
            merge_vimap_file_to_message(self.message, file, compressed)

        print("VIMap: loading sensors")
        with open(vimap_dir + '/sensors.yaml') as file:
            self.sensors = yaml.safe_load(file.read())

        print("VIMap: loading meta data")
        with open(vimap_dir + '/vi_map_metadata', 'r') as file:
            self.meta_data = text_format.Parse(file.read(), vi_map_pb2.VIMapMetadata())

    def save_to(self, map_dir: str, compressed: bool):
        vimap_dir = map_dir + '/vi_map'
        try:
            os.makedirs(vimap_dir)
        except FileExistsError:
            print("VImap: map directory appears to exist")
        else:
            print("VIMap: create new map directory")

        if 'resources' not in os.listdir(map_dir):
            os.mkdir(map_dir + "/resources")

        with open(map_dir + "/metadata", "w") as file:
            file.write(f"map_folder: \"{map_dir}\"\n"
                       f"resource_folder_in_use: -1\n"
                       f"map_resource_folder: \"{map_dir + '/resources/'}\"\n")

        with open(map_dir + "/resource_info", 'w') as file:
            file.write("")

        with open(vimap_dir + '/sensors.yaml', 'w') as file:
            file.write(yaml.safe_dump(self.sensors))

        file_type_list = [create_file_type(s) for s in ['missions', 'vertices', 'edges', 'landmark_index']]
        for file_type in file_type_list:
            self.save_data_of_file_type(vimap_dir, file_type, compressed)

        meta = vi_map_pb2.VIMapMetadata()
        meta.files.extend(file_type_list)
        with open(vimap_dir + '/vi_map_metadata', 'w') as file:
            file.write(text_format.MessageToString(meta))

    def save_data_of_file_type(self, vimap_dir: str, file_type, compressed: bool):
        msg = vi_map_pb2.VIMap()
        if file_type.file_type == 0:
            msg.missions.extend(self.message.missions)
            msg.mission_ids.extend(self.message.mission_ids)
            msg.mission_base_frames.extend(self.message.mission_base_frames)
            msg.mission_base_frame_ids.extend(self.message.mission_base_frame_ids)
        if file_type.file_type == 1:
            msg.vertex_ids.extend(self.message.vertex_ids)
            msg.vertices.extend(self.message.vertices)
        if file_type.file_type == 2:
            msg.edge_ids.extend(self.message.edge_ids)
            msg.edges.extend(self.message.edges)
        if file_type.file_type == 3:
            msg.landmark_index.extend(self.message.landmark_index)
            msg.landmark_index_ids.extend(self.message.landmark_index_ids)
        data = msg.SerializeToString()
        if compressed:
            data = gzip.compress(data)
        with open(vimap_dir + '/' + file_type.path, 'wb') as file:
            file.write(data)

# %%


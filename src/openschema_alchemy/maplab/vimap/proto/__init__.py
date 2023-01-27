import gzip
import os
import yaml
import numpy as np
from google.protobuf import text_format

from maplab.vimap.proto import vi_map_pb2


def tuple_from_id(aslam_id):
    return aslam_id.uint[0], aslam_id.uint[1]


def id_from_tuple(tuple_id):
    aslam_id = vi_map_pb2.aslam_dot_common_dot_id__pb2.Id()
    aslam_id.uint.extend(tuple_id)
    return aslam_id


def hex_string_from_tuple(tuple_id):
    id_uint64_array = np.array(tuple_id, dtype=np.uint64)
    id_char_array = np.frombuffer(id_uint64_array.data, dtype=np.uint8)
    hex_string = ""
    for c in id_char_array:
        hex_string += hex(c >> 4)[2]
        hex_string += hex(c & 0xf)[2]
    return hex_string


def tuple_from_hex_string(hex_string):
    assert len(hex_string) == 32, "Hash string must have length 32"
    id_char_array = np.array([int(hex_string[2*i:2*(i+1)], 16) for i in range(16)], dtype=np.uint8)
    id_uint64_array = np.frombuffer(id_char_array.data, dtype=np.uint64)
    return id_uint64_array[0], id_uint64_array[1]


def create_file_type(type_string: str, path=None):
    type_string_to_id = {"missions": 0, "vertices": 1, "edges": 2, "landmark_index": 3}
    if path is None:
        path = type_string
    ft = vi_map_pb2.FileTypeWithPath()
    ft.file_type = type_string_to_id[type_string]
    ft.path = path
    return ft


class VIMap:
    def __init__(self, map_dir: str = None, compressed: bool = True):
        self.message = vi_map_pb2.VIMap()
        self.sensors = None
        self.metadata = None
        self.resource_info = None
        self.resources = None
        self.vi_map_metadata = None
        if map_dir is not None:
            self.load_from(map_dir, compressed)

    def load_from(self, map_dir: str, compressed: bool = True):
        assert "vi_map" in os.listdir(map_dir), f"Cannot find 'vi_map' directory in path {map_dir}"
        vimap_dir = map_dir + "/vi_map"

        print("VIMap: loading meta data")
        with open(vimap_dir + "/vi_map_metadata", "r") as file:
            self.vi_map_metadata = text_format.Parse(file.read(), vi_map_pb2.VIMapMetadata())

        print("VIMap: loading data")
        self.message = vi_map_pb2.VIMap()
        for file in self.vi_map_metadata.files:
            self.merge_file_to_message(f"{vimap_dir}/{file.path}", compressed)

        print("VIMap: loading sensors")
        with open(vimap_dir + "/sensors.yaml", "r") as file:
            self.sensors = yaml.safe_load(file.read())

    def merge_file_to_message(self, file_name: str, compressed: bool):
        with open(file_name, "rb") as file:
            data = file.read()
        if compressed:
            data = gzip.decompress(data)
        self.message.MergeFromString(data)

    def save_to(self, map_dir: str, compressed: bool):
        vimap_dir = map_dir + "/vi_map"
        try:
            os.makedirs(vimap_dir)
        except FileExistsError:
            print("VImap: map directory appears to exist")
        else:
            print("VIMap: create new map directory")

        if "resources" not in os.listdir(map_dir):
            os.mkdir(map_dir + "/resources")

        with open(map_dir + "/metadata", "w") as file:
            file.write(f"map_folder: \"{map_dir}\"\n"
                       f"resource_folder_in_use: -1\n"
                       f"map_resource_folder: \"{map_dir}/resources\"\n")

        print("VIMap: saving resources")
        with open(map_dir + "/resource_info", "w") as file:
            file.write("")

        print("VIMap: saving sensors")
        with open(vimap_dir + "/sensors.yaml", "w") as file:
            file.write(yaml.safe_dump(self.sensors))

        print("VIMap: saving data")
        file_type_list = [create_file_type(s) for s in ["missions", "vertices", "edges", "landmark_index"]]
        for file_type in file_type_list:
            self.save_data_of_file_type(map_dir, file_type, compressed)

        print("VIMap: saving meta data")
        meta = vi_map_pb2.VIMapMetadata()
        meta.files.extend(file_type_list)
        with open(vimap_dir + "/vi_map_metadata", "w") as file:
            file.write(text_format.MessageToString(meta))

    def save_data_of_file_type(self, map_dir: str, file_type, compressed: bool):
        vimap_dir = map_dir + "/vi_map"
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
        with open(vimap_dir + "/" + file_type.path, "wb") as file:
            file.write(data)

    def add_loop_closure_edge(self, transform, transform_covariance,
                              switch_variable: float, switch_variable_variance: float,
                              from_vertex_id: tuple, to_vertex_id: tuple, edge_id: tuple):
        lc_edge = vi_map_pb2.LoopclosureEdge()
        lc_edge.T_A_B.extend(transform)
        lc_edge.T_A_B_covariance.extend(transform_covariance)
        lc_edge.__getattribute__("from").CopyFrom(id_from_tuple(from_vertex_id))
        lc_edge.__getattribute__("to").CopyFrom(id_from_tuple(to_vertex_id))
        lc_edge.switch_variable = switch_variable
        lc_edge.switch_variable_variance = switch_variable_variance
        edge = vi_map_pb2.Edge()
        edge.loopclosure.CopyFrom(lc_edge)
        self.message.edges.extend([edge])
        self.message.edge_ids.extend([id_from_tuple(edge_id)])

    def vertices(self):
        vertices = {}
        for vertex_id, vertex in zip(self.message.vertex_ids, self.message.vertices):
            vertices[tuple_from_id(vertex_id)] = vertex
        return vertices

    def edges(self):
        edges = {}
        for edge_id, edge in zip(self.message.edge_ids, self.message.edges):
            edges[tuple_from_id(edge_id)] = edge
        return edges

    def missions(self):
        missions = {}
        for mission_id, mission in zip(self.message.mission_ids, self.message.missions):
            missions[tuple_from_id(mission_id)] = mission
        return missions

    def mission_base_frames(self):
        mission_base_frames = {}
        for mission_base_frame_id, mission_base_frame in zip(self.message.mission_base_frame_ids, self.message.mission_base_frames):
            mission_base_frames[tuple_from_id(mission_base_frame_id)] = mission_base_frame
        return mission_base_frames

    def get_missions_timestamp_to_vertex_id_map(self) -> dict:
        missions_ts_id = {tuple_from_id(m_id): {} for m_id in self.message.mission_ids}
        for vertex_id, vertex in self.vertices().items():
            timestamp = vertex.n_visual_frame.frames[0].timestamp
            m_id = vertex.mission_id
            missions_ts_id[tuple_from_id(m_id)][timestamp] = vertex_id
        return missions_ts_id


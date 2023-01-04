import gzip
import os
import yaml
from glob import glob

from maplab.vimap.proto import vi_map_pb2


def merge_vimap_file_to_message(message: vi_map_pb2.VIMap, file_name: str, compressed: bool) -> vi_map_pb2.VIMap:
    with open(file_name, 'rb') as file:
        data = file.read()
    if compressed:
        data = gzip.decompress(data)
    message.MergeFromString(data)


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

        with open(vimap_dir + '/sensors.yaml') as file:
            self.sensors = yaml.safe_load(file.read())

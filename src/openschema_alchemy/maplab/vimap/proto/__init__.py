import gzip
import os
from glob import glob

from maplab.vimap.proto import vi_map_pb2


def merge_vimap_file(message: vi_map_pb2.VIMap, file_name: str, compressed: bool) -> vi_map_pb2.VIMap:
    with open(file_name, 'rb') as file:
        data = file.read()
    if compressed:
        data = gzip.decompress(data)
    message.MergeFromString(data)


class VImap:
    def __init__(self, map_dir: str, compressed=True):
        assert 'vi_map' in os.listdir(map_dir), f"Cannot find 'vi_map' directory in path {map_dir}"
        vimap_dir = map_dir + '/vi_map'
        compressed = compressed

        print("VImap: loading data")
        self.message = vi_map_pb2.VIMap()
        merge_vimap_file(self.message, vimap_dir + '/missions', compressed)
        merge_vimap_file(self.message, vimap_dir + '/landmark_index', compressed)
        for file in glob(vimap_dir + '/edges*') + glob(vimap_dir + '/vertices*'):
            merge_vimap_file(self.message, file, compressed)

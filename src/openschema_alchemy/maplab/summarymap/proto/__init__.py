import gzip
import numpy as np

from maplab.summarymap.proto import summary_map_pb2


class SummaryMap:
    """
    Summary map is essentially a bipartite graph of landmarks and observers (the two classes of vertices)
     where the edges encode the visibility (between landmarks and observers).
     Each landmark and observer has a unique position.
     Each visibility edge has a unique descriptor.
    """
    def __init__(self, map_dir: str, compressed=True):
        print("SummaryMap: loading data")
        with open(map_dir + '/localization_summary_map', 'rb') as file:
            data = file.read()
        if compressed:
            data = gzip.decompress(data)
        self._message = summary_map_pb2.LocalizationSummaryMap()
        self._message.ParseFromString(data)

        # load landmarks
        landmarks_position = np.array(self._message.G_landmark_position)
        landmarks_num = int(len(landmarks_position)/3)
        self.landmarks_position = landmarks_position.reshape(landmarks_num, 3)

        # load observers
        uncompressed_map = self._message.uncompressed_map
        observers_position = np.array(uncompressed_map.G_observer_position)
        observers_num = int(len(observers_position)/3)
        self.observers_positions = observers_position.reshape(observers_num, 3)

        # load visibility edges
        # matrix: rows (visibility edges), columns (0: landmark index, 1: observer index)
        descriptor_to_landmark = np.expand_dims(np.array(uncompressed_map.observation_to_landmark_index), 1)
        descriptor_to_observer = np.expand_dims(np.array(uncompressed_map.observer_indices), 1)
        self.visibility_edges = np.append(descriptor_to_landmark, descriptor_to_observer, axis=1)

        # load descriptors of visibility edges
        # matrix: rows (visibility edges), columns (descriptor space)
        descriptors = uncompressed_map.descriptors
        # note descriptor data is stored in column-major format, hence cols and rows are switched
        self.visibility_edges_descriptor = np.array(descriptors.data).reshape(descriptors.cols, descriptors.rows)

        # utility dictionaries collecting connected vertices
        self.observers_by_landmark = {}
        self.landmarks_by_observer = {}
        for edge in self.visibility_edges:
            self.observers_by_landmark.setdefault(edge[0], []).append(edge[1])
            self.landmarks_by_observer.setdefault(edge[1], []).append(edge[0])

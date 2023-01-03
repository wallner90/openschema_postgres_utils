import gzip
import numpy as np
import os

from maplab.summarymap.proto import summary_map_pb2


def set_to_list_and_index_map(set_: set):
    list_ = list(set_)
    index_map = {}
    for i, ob in enumerate(list_):
        index_map[ob] = i
    return list_, index_map


class SummaryMap:
    """
    Summary map is essentially a bipartite graph of landmarks and observers (the two classes of vertices)
     where the edges encode the visibility (between landmarks and observers).
     Each landmark and observer has a unique position.
     Each visibility edge has a unique descriptor.
    """
    def __init__(self, map_dir: str = None, compressed: bool = True):
        self.map_dir = None
        self.landmarks_position = None
        self.observers_position = None
        self.visibility_edges = None
        self.visibility_edges_descriptor = None
        self._message = None

        if map_dir is not None:
            self.load(map_dir, compressed=compressed)

    def load(self, map_dir: str, compressed: bool = True):
        self.map_dir = map_dir
        print(f"Summary map: loading data from directory '{map_dir}'")
        with open(self.map_dir + '/localization_summary_map', 'rb') as file:
            data = file.read()
        if compressed:
            data = gzip.decompress(data)
        self._message = summary_map_pb2.LocalizationSummaryMap()
        self._message.ParseFromString(data)

        # load landmarks
        landmarks_position = np.array(self._message.G_landmark_position)
        landmarks_num = int(len(landmarks_position) / 3)
        self.landmarks_position = landmarks_position.reshape(landmarks_num, 3)

        # load observers
        uncompressed_map = self._message.uncompressed_map
        observers_position = np.array(uncompressed_map.G_observer_position)
        observers_num = int(len(observers_position) / 3)
        self.observers_position = observers_position.reshape(observers_num, 3)

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

    def save(self, map_dir: str, compressed: bool = True):
        self.map_dir = map_dir
        if os.path.exists(map_dir):
            print(f"Summary map: saving data into existing directory '{map_dir}'.")
        else:
            print(f"Summary map: saving data into new directory '{map_dir}'.")
            os.mkdir(map_dir)
        self._generate_message()
        data = self._message.SerializeToString()
        if compressed:
            data = gzip.compress(data)
        with open(self.map_dir + '/localization_summary_map', 'wb') as file:
            file.write(data)

    def observers_by_landmark(self):
        observers = {}
        for edge in self.visibility_edges:
            observers.setdefault(edge[0], set()).add(edge[1])
        return observers

    def landmarks_by_observers(self):
        landmarks = {}
        for edge in self.visibility_edges:
            landmarks.setdefault(edge[1], set()).add(edge[0])
        return landmarks

    def submap_from_observers(self, observers: set):
        # collect all observed landmarks
        landmarks_by_all_observers = self.landmarks_by_observers()
        landmarks_by_observers = {ob: landmarks_by_all_observers[ob] for ob in observers}
        landmarks = set()
        for lms in landmarks_by_observers.values():
            landmarks = landmarks.union(lms)

        submap = SummaryMap()
        observer_list, observer_index = set_to_list_and_index_map(observers)
        submap.observers_position = self.observers_position[observer_list]
        landmark_list, landmark_index = set_to_list_and_index_map(landmarks)
        submap.landmarks_position = self.landmarks_position[landmark_list]

        # collect the corresponding visibility edges
        visibility_edges = []
        visibility_edges_descriptor = []
        for edge_index, edge in enumerate(self.visibility_edges):
            if edge[0] in landmarks and edge[1] in observers:
                visibility_edges += [(landmark_index[edge[0]], observer_index[edge[1]])]
                visibility_edges_descriptor += [self.visibility_edges_descriptor[edge_index]]
        submap.visibility_edges = np.array(visibility_edges)
        submap.visibility_edges_descriptor = np.array(visibility_edges_descriptor)
        return submap

    def submap_from_landmarks(self, landmarks: set):
        # collect all observers
        observers_by_all_landmarks = self.observers_by_landmark()
        observers_by_landmarks = {lm: observers_by_all_landmarks[lm] for lm in landmarks}
        observers = set()
        for obs in observers_by_landmarks.values():
            observers = observers.union(obs)

        submap = SummaryMap()
        observer_list, observer_index = set_to_list_and_index_map(observers)
        submap.observers_position = self.observers_position[observer_list]
        landmark_list, landmark_index = set_to_list_and_index_map(landmarks)
        submap.landmarks_position = self.landmarks_position[landmark_list]

        # collect the corresponding visibility edges
        visibility_edges = []
        visibility_edges_descriptor = []
        for edge_index, edge in enumerate(self.visibility_edges):
            if edge[0] in landmarks and edge[1] in observers:
                visibility_edges += [(landmark_index[edge[0]], observer_index[edge[1]])]
                visibility_edges_descriptor += [self.visibility_edges_descriptor[edge_index]]
        submap.visibility_edges = np.array(visibility_edges)
        submap.visibility_edges_descriptor = np.array(visibility_edges_descriptor)
        return submap

    def _generate_message(self):
        descriptors_msg = summary_map_pb2.maplab__common_dot_eigen__pb2.MatrixXf()
        descriptors_msg.data.extend([d for d in self.visibility_edges_descriptor.flatten()])
        descriptors_msg.cols = self.visibility_edges_descriptor.shape[0]
        descriptors_msg.rows = self.visibility_edges_descriptor.shape[1]

        uncompressed_map_msg = summary_map_pb2.UncompressedLocalizationSummaryMap()
        uncompressed_map_msg.descriptors.CopyFrom(descriptors_msg)
        uncompressed_map_msg.G_observer_position.extend([p for p in self.observers_position.flatten()])
        uncompressed_map_msg.observer_indices.extend([e[1] for e in self.visibility_edges])
        uncompressed_map_msg.observation_to_landmark_index.extend([e[0] for e in self.visibility_edges])

        self._message = summary_map_pb2.LocalizationSummaryMap()
        self._message.G_landmark_position.extend([p for p in self.landmarks_position.flatten()])
        self._message.uncompressed_map.CopyFrom(uncompressed_map_msg)

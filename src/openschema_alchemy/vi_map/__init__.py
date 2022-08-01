import pandas as pd
import os
import re


def format_columns(df):
    units = [x.group().strip()[1:-1] if x is not None else '' for x in [re.search('\[.*\]', x) for x in df.columns]]
    df.columns = [re.sub(' ', '_', re.sub('\[.*\]', '', x).strip()) for x in df.columns]

    return df, units


class VImap:

    def __init__(self, vimap_dir):
        self.dir = vimap_dir
        self.mission = os.path.basename(vimap_dir)

        self.descriptor = pd.read_csv('{}/descriptor.csv'.format(self.dir), header=None)
        self.imu, self.imu_units = format_columns(pd.read_csv('{}/imu.csv'.format(self.dir)))
        self.landmarks, self.landmark_units = format_columns(pd.read_csv('{}/landmarks.csv'.format(self.dir)))
        self.observations, self.observations_units = format_columns(pd.read_csv('{}/observations.csv'.format(self.dir)))
        self.tracks, self.tracks_units = format_columns(pd.read_csv('{}/tracks.csv'.format(self.dir))[1:])
        self.vertices, self.vertices_units = format_columns(pd.read_csv('{}/vertices.csv'.format(self.dir)))

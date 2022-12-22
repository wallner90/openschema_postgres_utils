import pandas as pd
from io import StringIO
import os
import re


def format_columns_and_extract_units(df):
    # extract units of columns: 'column name [unit]' -> 'unit'
    units = [x.group().strip()[1:-1] if x is not None else '' for x in [re.search('\[.*\]', x) for x in df.columns]]
    # reformat column names to use as members variables: 'column name [unit]' -> 'column_name'
    formatted_columns = [re.sub(' ', '_', re.sub('\[.*\]', '', x).strip()) for x in df.columns]
    df.columns = formatted_columns
    return df, units


class VImap:

    def __init__(self, vimap_dir):
        self.dir = vimap_dir
        self.mission = os.path.basename(vimap_dir)

        with open(f'{vimap_dir}/descriptor.csv') as file:
            # we need to skip the first line, which notes "Descriptor byte as integer 1-N"
            text = file.readlines()
            text.pop(0)
            self.descriptor = pd.DataFrame(text)
        self.observations, _ = format_columns_and_extract_units(pd.read_csv(f'{vimap_dir}/observations.csv'))
        self.imu, self.imu_units = format_columns_and_extract_units(pd.read_csv(f'{vimap_dir}/imu.csv'))
        self.landmarks, self.landmark_units = format_columns_and_extract_units(pd.read_csv(f'{vimap_dir}/landmarks.csv'))
        self.keypoint_tracks, self.keypoint_tracks_units = format_columns_and_extract_units(pd.read_csv(f'{vimap_dir}/tracks.csv'))
        self.vertices, self.vertices_units = format_columns_and_extract_units(pd.read_csv(f'{vimap_dir}/vertices.csv'))

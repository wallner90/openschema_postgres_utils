# img_viewer.py

import PySimpleGUI as sg

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker, close_all_sessions
from sqlalchemy import create_engine, text, inspect

from rasterio.io import MemoryFile
from rasterio.plot import show
from rasterio import open as raster_open
from rasterio.enums import ColorInterp

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import numpy as np

from datetime import datetime

from sqlalchemy.dialects.postgresql import JSON

from model import *

import matplotlib
# matplotlib.use('TkAgg')


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def main():

    default_connection_uri = "postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait"
    active_schema = None

    engine = None
    Session = None
    session = None

    assigned_rois = {}
    unassigned_rois = {}

    connection_input_line = [
        sg.Text("Connection:", size=(10, 1)),
        sg.InputText(default_text=default_connection_uri,
                     key="-CONNECTION-URI-"),
        sg.Button("connect",
                  key="-CONNECT-",
                  size=(10, 1)),
    ]
    schemas_drop_down_line = [
        sg.Text("Schema:", size=(10, 1)),
        sg.DropDown([""],
                    key="-SCHEMAS-DROP-DOWN-",
                    readonly=True,
                    disabled=True),
        sg.Button("select", key="-SELECT-SCHEMA-",
                  disabled=True,
                  size=(10, 1)),
    ]
    choose_assigned_roi = [
        sg.Text("Assigned ROIs:", size=(15, 1)),
        sg.DropDown([""],
                    key="-ASSIGNED-ROI-DROP-DOWN-",
                    size=(20, 1),
                    readonly=True,
                    disabled=True),
        sg.Button("view", key="-VIEW-ASSIGNED-ROI-",
                  disabled=True,
                  size=(10, 1)),
    ]
    choose_unassigned_roi = [
        sg.Text("Unassigned ROIs:", size=(15, 1)),
        sg.DropDown([""],
                    key="-UNASSIGNED-ROI-DROP-DOWN-",
                    size=(20, 1),
                    readonly=True,
                    disabled=True),
        sg.Button("assign", key="-ASIGN-UNASSIGNED-ROI-",
                  disabled=True,
                  size=(10, 1)),
    ]

    input_column = [
        connection_input_line,
        schemas_drop_down_line,
        choose_assigned_roi,
        choose_unassigned_roi
    ]

    image_viewer_column = [
        [
            sg.Text("Pile ROI View"),
            sg.Canvas(key="-CANVAS-")
        ]
    ]

    layout = [
        [
            sg.Column(input_column),
            sg.VerticalSeparator(),
            sg.Column(image_viewer_column)
        ]
    ]

    window = sg.Window("openSCHEMA GUI", layout, resizable=True,
                       finalize=True, size=(800, 300))
    window["-CONNECTION-URI-"].expand(expand_x=True)
    window["-SCHEMAS-DROP-DOWN-"].expand(expand_x=True)

    # Run the Event Loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "-CONNECT-":
            close_all_sessions()
            engine = create_engine(values["-CONNECTION-URI-"])
            try:
                engine.connect()
            except:
                close_all_sessions()
                engine = None
                window["-CONNECTION-URI-"].update(background_color="orange")
                window["-SELECT-SCHEMA-"].update(disabled=True)
                window["-SCHEMAS-DROP-DOWN-"].update(values=[], disabled=True)
                sg.popup("Connection URI is invalid!")
                continue
            Session = sessionmaker(bind=engine)
            session = Session()
            try:
                window["-SCHEMAS-DROP-DOWN-"].update(
                    values=[*inspect(engine).get_schema_names()], disabled=False)
            except:
                window["-SCHEMAS-DROP-DOWN-"].update(
                    values=[], disabled=False)
            window["-CONNECTION-URI-"].update(background_color="green")
            window["-SELECT-SCHEMA-"].update(disabled=False)

        elif event == "-SELECT-SCHEMA-":
            active_schema = values["-SCHEMAS-DROP-DOWN-"]
            if not active_schema:
                continue
            try:
                for obj in session.query(Landmark).filter(text("descriptor->>'type' = 'pile'")).all():
                    if obj.semantic_geometries:
                        assigned_rois.setdefault(
                            obj.descriptor['pile_nr'], []).append(obj)
                    else:
                        unassigned_rois.setdefault(
                            obj.descriptor['pile_nr'], []).append(obj)

                if assigned_rois:
                    roi_identifier = [
                        f"Type: {val[0].descriptor['type']}, ID: {val[0].descriptor['pile_nr']}" for val in assigned_rois.values()]
                    window["-ASSIGNED-ROI-DROP-DOWN-"].update(
                        values=roi_identifier, disabled=False)
                    window["-VIEW-ASSIGNED-ROI-"].update(disabled=False)
                
                if unassigned_rois:
                    roi_identifier = [
                        f"Type: {val[0].descriptor['type']}, ID: {val[0].descriptor['pile_nr']}" for val in unassigned_rois.values()]
                    window["-UNASSIGNED-ROI-DROP-DOWN-"].update(
                        values=roi_identifier, disabled=False)
                    window["-ASIGN-UNASSIGNED-ROI-"].update(disabled=False)


                # get_raster_query = text(
                #     "SELECT ST_AsGDALRaster(ST_Union(ST_Clip(r.rast, p.polygon)), 'GTIFF') FROM ortho_raster_indexed r, piles p WHERE ST_Intersects(r.rast, p.polygon)")
                # results = session.execute(get_raster_query).one()

                get_raster_query = text(
                                    "SELECT ST_AsGDALRaster(ST_Union(r.rast), 'JPEG', ARRAY['QUALITY=50']) FROM ortho_raster_indexed r"
                                    )
                results = session.execute(get_raster_query).one()
                in_mem_file = MemoryFile(bytes(results[0]))
                in_mem_raster = in_mem_file.open()
                test = np.array(in_mem_raster.read()).T
                # show(in_mem_raster) # <- in Geo Coords

                # fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
                fig = plt.figure()
                plt.imshow(test)
                draw_figure(window["-CANVAS-"].TKCanvas, fig)

                # pyplot.imshow(test)   # <- w/ correct color coding

            except:
                True

    window.close()

    engine = create_engine(
        "postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait")
    Session = sessionmaker(bind=engine)
    session = Session()

    get_raster_query = text(
        "SELECT ST_AsGDALRaster(ST_Union(ST_Clip(r.rast, p.polygon)), 'GTIFF') FROM ortho_raster_indexed r, piles p WHERE ST_Intersects(r.rast, p.polygon)")
    results = session.execute(get_raster_query).one()
    in_mem_file = MemoryFile(bytes(results[0]))
    in_mem_raster = in_mem_file.open()
    test = np.array(in_mem_raster.read()).T
    # show(in_mem_raster) # <- in Geo Coords
    # pyplot.imshow(test)   # <- w/ correct color coding

    piles = {}
    for obj in session.query(Landmark).filter(text("descriptor->>'type' = 'pile'")).all():
        if not obj.semantic_geometries:
            piles.setdefault(obj.descriptor['pile_nr'], []).append(obj)

    ts = datetime.utcnow()
    map = Map(name='sem_polygon_map_3',
              description={"T_global": [
                  0.0]*12, "AuthorithyID": "EPSG:25833", "CRS": "ETRS89 / UTM zone 33N"},
              created_at=ts, updated_at=ts)
    pg = PoseGraph(name="Virtual roi pose graph", map=map,
                   description={})
    # all (virtual) keypoints share the same (virtual) pose for semantic_observation
    pose = Pose(position=f"POINTZ({0} {0} {0})", posegraph=pg)
    semantic_observation = SemanticObservation(
        pose=pose, algorithm="qgis_points", created_at=ts, updated_at=ts,
        algorithm_settings={"qgis_points":
                            {"test": 123,
                             }})

    connections = []
    sem_geoms = []
    kps = []

    for nr, pile in piles.items():
        sem_geom = SemanticPolygon(type=SemanticGeometryType.Polygon.value, description={
                                   'type': 'pile', 'pile_nr': nr, 'description': 'A pile in Kieswerk Asten.'})
        sem_geoms.append(sem_geom)
        for lm in pile:
            kps.append(SemanticKeypoint(
                observation=semantic_observation, landmark=lm))
            connection = ManyLandmarkHasManySemanticGeometry(
                landmark=lm,
                order_idx=lm.descriptor['corner_id']
            )
            sem_geom.landmarks.append(connection)
            connections.append(connection)
            print("test")
        # create semantic geometry

    session.add_all(connections + sem_geoms + kps +
                    [map, pg, pose, semantic_observation])
    session.commit()

    print("test")


if __name__ == '__main__':
    main()

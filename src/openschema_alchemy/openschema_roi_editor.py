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

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

import numpy as np

import re

from datetime import datetime

from sqlalchemy.dialects.postgresql import JSON
from geoalchemy2.shape import to_shape

from shapely.geometry import MultiPoint

from model import *

import matplotlib
# matplotlib.use('TkAgg')


def draw_figure(canvas, figure):
    # canvas.pack_forget()
    canvas.delete()
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)
    # canvas.pack()
    return figure_canvas_agg


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


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
                # get all unassigned landmarks
                unassigned_lms = session.query(Landmark).filter(
                    Landmark.keypoints == None).filter(
                    Landmark.semantic_geometries == None).all()
                #unassigned_lms_point_dict = {to_shape(elem.position).xy : elem for elem in unassigned_lms}
                points = [to_shape(landmark.position) for landmark in unassigned_lms]
                if points:
                    ts = datetime.utcnow()
                    map = Map(name=f'qgis_roi_editor_map_{ts}',
                            description={"T_global": [
                                0.0]*12, "AuthorithyID": "EPSG:25833", "CRS": "ETRS89 / UTM zone 33N"},
                            created_at=ts, updated_at=ts)
                    pg = PoseGraph(name="Virtual roi pose graph for qgis import", map=map,
                                description={})
                    pose = Pose(position=f"POINTZ({0} {0} {0})", posegraph=pg)
                    semantic_observation = SemanticObservation(
                        pose=pose, algorithm="qgis_points", created_at=ts, updated_at=ts,
                        algorithm_settings={"qgis_points":
                                            {"version": "0.1",
                                            }})
                    
                    sem_geom = SemanticPolygon(description={
                                   'type': 'pile', 'pile_nr': 5, 'description': 'A pile in Kieswerk Asten.'})
                    connections = []
                    sem_geoms = []
                    kps = []
                    lms = []

                    convex_hull_pts = list(MultiPoint(points).convex_hull.exterior.coords)
                    for idx, convex_hull_pt in enumerate(convex_hull_pts):
                        lm = Landmark(
                            position=f"POINTZ({convex_hull_pt[0]} {convex_hull_pt[1]} {convex_hull_pt[2]})",
                            descriptor={"type": "pile"})
                        lms.append(lm)
                        kps.append(SemanticKeypoint(
                        observation=semantic_observation, landmark=lm))
                        connection = ManyLandmarkHasManySemanticGeometry(
                            landmark=lm,
                            order_idx=idx)
                        sem_geom.landmarks.append(connection)
                        connections.append(connection)

                    session.add_all(connections + sem_geoms + kps +
                                    [map, pg, pose, semantic_observation])                    

                    for lm in unassigned_lms:
                        session.delete(lm)
                    session.commit()

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

            except:
                True

        elif event == "-VIEW-ASSIGNED-ROI-":
            if assigned_rois:

                chosen_pile = values["-ASSIGNED-ROI-DROP-DOWN-"]
                pattern = r'ID:\s*(\d+)'
                match = re.search(pattern, chosen_pile)
                if match:
                    id = int(match.group(1))
                    if id in assigned_rois.keys():
                        get_raster_query = text(f"SELECT p.pile_nr, ST_AsGDALRaster(ST_Union(ST_Clip(r.rast, p.polygon)), 'GTIFF') AS raster \
                                                FROM ortho_raster_indexed r, piles p \
                                                WHERE ST_Intersects(r.rast, p.polygon) AND p.pile_nr = {id} \
                                                GROUP BY p.pile_nr")
                        result = session.execute(get_raster_query).one()
                        in_mem_file = MemoryFile(bytes(result.raster))
                        in_mem_raster = in_mem_file.open()
                        plt.ion()
                        plt.figure()
                        fig = plt.gcf()
                        fig.clear()
                        pile_img = np.array(in_mem_raster.read()).T
                        plt.imshow(pile_img)
                        draw_figure(window["-CANVAS-"].TKCanvas, fig)

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

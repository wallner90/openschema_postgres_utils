# img_viewer.py

import PySimpleGUI as sg
import os.path

from sqlalchemy import create_engine, text, inspect, select, func
from sqlalchemy.orm import sessionmaker, close_all_sessions
# not directly "used", but needed for introspection !DO NOT REMOVE!
from geoalchemy2 import Geometry
from model import *
import open3d as o3d


def main():

    default_connection_uri = "postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait"
    active_schema = None

    exportable_elements = ["Pose", "Landmark"]

    engine = None
    Session = None
    session = None

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
    map_drop_down_line = [
        sg.Text("Map:", size=(10, 1)),
        sg.DropDown([""],
                    key="-MAPS-DROP-DOWN-",
                    readonly=True,
                    disabled=True),
        sg.Button("select", key="-SELECT-MAP-",
                  disabled=True,
                  size=(10, 1)),
    ]

    element_select_lines = [
        [
            sg.Text(f"{elem}:"),
            sg.Text("( "),
            sg.Text("0", key=f"-CHECKBOX-{elem.upper()}-COUNT-TEXT-"),
            sg.Text(" )"),
            sg.Input(),
            sg.FileSaveAs(button_text="browse",
                          key=f"-SAVE-{elem.upper()}-AS-DIALOG-", disabled=True),
            sg.Button(
                "save", key=f"-SAVE-{elem.upper()}-BUTTON-", disabled=True)
        ] for elem in exportable_elements
    ]

    layout = [[
        connection_input_line,
        [*schemas_drop_down_line,
         sg.VerticalSeparator(),
         *map_drop_down_line],
        element_select_lines,
    ]]

    window = sg.Window("openSCHEMA GUI", layout, resizable=True,
                       finalize=True)
    window["-CONNECTION-URI-"].expand(expand_x=True)
    window["-SCHEMAS-DROP-DOWN-"].expand(expand_x=True)
    window["-MAPS-DROP-DOWN-"].expand(expand_x=True)

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
                    values=[], disabled=True)
            window["-CONNECTION-URI-"].update(background_color="green")
            window["-SELECT-SCHEMA-"].update(disabled=False)

        elif event == "-SELECT-SCHEMA-":
            active_schema = values["-SCHEMAS-DROP-DOWN-"]
            if not active_schema:
                continue
            try:
                window["-MAPS-DROP-DOWN-"].update(
                    values=[x.name for x in session.query(Map).all()], disabled=False)
                window["-SELECT-MAP-"].update(disabled=False)
            except:
                window["-MAPS-DROP-DOWN-"].update(
                    values=[], disabled=True)
                window["-SELECT-MAP-"].update(disabled=True)

        elif event == "-SELECT-MAP-":
            active_map = values["-MAPS-DROP-DOWN-"]
            if not active_map:
                continue
            try:
                map = session.query(Map).filter(Map.name == active_map).one()
                poses = map.posegraphs[0].poses
                num_landmarks = session.query(Landmark).join(Keypoint).join(
                    Observation, Keypoint.observation_id == Observation.id).join(
                    Pose).join(PoseGraph).join(Map).filter(Map.name == active_map).count()
                window["-CHECKBOX-POSE-COUNT-TEXT-"].update(
                    value=f"{len(poses)}")
                window["-CHECKBOX-LANDMARK-COUNT-TEXT-"].update(
                    value=f"{num_landmarks}")
                for exp_elem in exportable_elements:
                    window[f"-SAVE-{exp_elem.upper()}-AS-DIALOG-"].update(disabled=False)
                    window[f"-SAVE-{exp_elem.upper()}-BUTTON-"].update(disabled=False)
            except:
                pass

        elif event == "-SAVE-POSE-BUTTON-":
            out_file = values["-SAVE-POSE-AS-DIALOG-"]
            pcd = o3d.geometry.PointCloud()
            map = session.query(Map).filter(Map.name == active_map).one()
            poses = map.posegraphs[0].poses
            poses_out = [session.execute(select(func.ST_X(pose.position), func.ST_Y(
                pose.position), func.ST_Z(pose.position))).one() for pose in poses]
            pcd.points = o3d.utility.Vector3dVector(poses_out)
            o3d.io.write_point_cloud(out_file, pcd)

        elif event == "-SAVE-LANDMARK-BUTTON-":
            out_file = values["-SAVE-LANDMARK-AS-DIALOG-"]
            pcd = o3d.geometry.PointCloud()
            map = session.query(Map).filter(Map.name == active_map).one()
            lms = session.query(Landmark).join(Keypoint).join(Observation).join(Pose).join(PoseGraph).join(Map).filter(Map.name == active_map).all()
            lms_out = [session.execute(select(func.ST_X(lm.position), func.ST_Y(
                lm.position), func.ST_Z(lm.position))).one() for lm in lms]
            pcd.points = o3d.utility.Vector3dVector(lms_out)
            o3d.io.write_point_cloud(out_file, pcd)
    window.close()


if __name__ == '__main__':
    main()

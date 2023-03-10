# img_viewer.py

import PySimpleGUI as sg
import os.path

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, close_all_sessions
# not directly "used", but needed for introspection !DO NOT REMOVE!
from geoalchemy2 import Geometry


def main():

    default_connection_uri = "postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait"
    active_schema = None
    table_details_columns = ['name', 'type', 'nullable',
                             'default', 'autoincrement', 'comment']

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
    tables_drop_down_line = [
        sg.Text("Table:", size=(10, 1)),
        sg.DropDown([""],
                    key="-TABLES-DROP-DOWN-",
                    readonly=True,
                    disabled=True),
        sg.Button("select", key="-SELECT-TABLE-",
                  disabled=True,
                  size=(10,1)),
    ]
    table_view = [
        sg.Table(values=[[]],
                 key="-TABLE-DETAIL-VIEW-",
                 headings=table_details_columns, auto_size_columns=True, max_col_width=100)
    ]
    # table_view_col = sg.Column([table_view])

    layout = [[
        connection_input_line,
        schemas_drop_down_line,
        tables_drop_down_line,
        table_view
    ]]

    window = sg.Window("openSCHEMA GUI", layout, resizable=True,
                       finalize=True, size=(1024,400))
    window["-CONNECTION-URI-"].expand(expand_x=True)
    window["-SCHEMAS-DROP-DOWN-"].expand(expand_x=True)
    window["-TABLES-DROP-DOWN-"].expand(expand_x=True)
    window["-TABLE-DETAIL-VIEW-"].expand(expand_x=True, expand_y=True, expand_row=True)
    # window["-TABLE-DETAIL-VIEW-"].expand(True, True)
    # table_view_col.expand(True, True)

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
                window["-TABLES-DROP-DOWN-"].update(values=[], disabled=True)
                window["-SELECT-TABLE-"].update(disabled=True)
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
                window["-TABLES-DROP-DOWN-"].update(
                    values=[*inspect(engine).get_table_names(schema=active_schema)], disabled=False)
                window["-SELECT-TABLE-"].update(disabled=False)
            except:
                window["-TABLES-DROP-DOWN-"].update(
                    values=[], disabled=False)
                window["-SELECT-TABLE-"].update(disabled=True)
        elif event == "-SELECT-TABLE-":
            table_info = []
            try:
                table_info = inspect(engine).get_columns(
                    values["-TABLES-DROP-DOWN-"])
            except:
                pass
            values = []
            for item in table_info:
                row = [item[key] for key in table_details_columns]
                values.append(row)
            window["-TABLE-DETAIL-VIEW-"].update(values=values)
            # table_view_col.expand(True, True)
            # window["-TABLE-DETAIL-VIEW-"].expand(True, True)

    window.close()


if __name__ == '__main__':
    main()

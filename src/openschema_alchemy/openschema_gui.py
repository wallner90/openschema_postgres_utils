# img_viewer.py

import PySimpleGUI as sg
import os.path

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, close_all_sessions
# not directly "used", but needed for introspection !DO NOT REMOVE!
from geoalchemy2 import Geometry

default_connection_uri = "postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait"
default_schema = "public"
table_details_columns = ['name', 'type', 'nullable',
                         'default', 'autoincrement', 'comment']


engine = None
Session = None
session = None

connection_input_line = [
    sg.Text("Connection:"),
    sg.InputText(default_text=default_connection_uri, size=(
        70, 1), key="-CONNECTION-URI-"),
    sg.Button("connect", key="-CONNECT-"),
]
schemas_drop_down_line = [
    sg.Text("Schema:"),
    sg.DropDown(["---"],
                key="-SCHEMAS-DROP-DOWN-",
                default_value=["---"],
                readonly=True,
                size=(50, 1),
                disabled=True),
    sg.Button("select", key="-SELECT-SCHEMA-",
              disabled=True),
]
tables_drop_down_line = [
    sg.Text("Table:"),
    sg.DropDown(["---"],
                key="-TABLES-DROP-DOWN-",
                default_value=["---"],
                readonly=True,
                size=(50, 1),
                disabled=True),
    sg.Button("select", key="-SELECT-TABLE-",
              disabled=True),
]
table_view = [
    sg.Table(values=[[]],
             key="-TABLE-DETAIL-VIEW-",
             headings=table_details_columns, auto_size_columns=True, max_col_width=100)
    # sg.Text("Table Elements")
]
table_view_col = sg.Column([table_view])

# layout = [[
#     sg.Column([
#         connection_input_line,
#         schemas_drop_down_line,
#         tables_drop_down_line,
#     ]),
#     sg.VSeperator(),
#     table_view_col
# ]]

layout = [[
    connection_input_line,
    schemas_drop_down_line,
    tables_drop_down_line,
    table_view_col
]]

window = sg.Window("openSCHEMA GUI", layout, auto_size_text=True,
                   auto_size_buttons=True, resizable=True,
                   border_depth=5, finalize=True)
window["-TABLE-DETAIL-VIEW-"].expand(True, True)
table_view_col.expand(True, True)


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
        default_schema = values["-SCHEMAS-DROP-DOWN-"]
        try:
            window["-TABLES-DROP-DOWN-"].update(
                values=[*inspect(engine).get_table_names(schema=default_schema)], disabled=False)
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
        table_view_col.expand(True, True)
        window["-TABLE-DETAIL-VIEW-"].expand(True, True)

window.close()

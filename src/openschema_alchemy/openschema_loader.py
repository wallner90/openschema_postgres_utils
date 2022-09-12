import argparse
from pathlib import Path
from xmlrpc.client import Boolean
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import sessionmaker

import openschema_utils
import model
import openVSLAM_io
import lane_map_json_to_db as lanemap_io
import lidar_karte_to_db as lidar_io


def main():
    file_formats = ["openVSLAM", "maplab", "lanemap", "lidar"]
    parser = argparse.ArgumentParser(
        description="openSCHEMA data loader: Load and store data to postgreSQL database.")
    parser.add_argument("-m", "--mode", type=str, choices=["to_file", "to_db"], required=True,
                        help="Use 'to_file' to fetch data from the database to the given format, or 'to_db' to push data into the database.")
    parser.add_argument("-f", "--format", type=str, choices=file_formats, required=True,
                        help="Dataformat of the file given using '--output_file' or '--input_file' resp.")
    parser.add_argument("-c", "--db_connection", type=str,
                        default="postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait", help="URI of the database to connect to.")
    parser.add_argument("-n", "--map_name", type=str)
    parser.add_argument("-o", "--output_file", type=str,
                        help="Full path to output file if 'to_file' is chosen'.")
    parser.add_argument("-i", "--input_file", type=str,
                        help="Full path to input file if 'to_db' is chosen'.")
    parser.add_argument("--create_public_schema", action='store_true',
                        help="For 'to_db' mode only: Create schema 'public' if it does not exist.")
    args = parser.parse_args()
    if not openschema_utils.args_sanity_check(args):
        return

    engine = create_engine(args.db_connection)
    if args.mode == "to_db" and args.create_public_schema == True:
        if not engine.dialect.has_schema(engine, 'public'):
            engine.execute(CreateSchema('public'))
        model.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if args.format == "openVSLAM":
        if args.mode == "to_file":
            print("INFO: Load data from database into openVSLAM format...")
            openVSLAM_io.to_file(session=session,
                               output_file=args.output_file,
                               map_name=args.map_name)
        elif args.mode == "to_db":
            print("INFO: Load data from openVSLAM format into database...")
            openVSLAM_io.to_db(session=session,
                               input_file=args.input_file,
                               map_name=args.map_name)
    if args.format == "maplab":
        if args.mode == "to_db":
            print("WARNING: Not implemented yet: store into maplab format from db.")
        elif args.mode == "to_db":
            print("WARNING: Not implemented yet: store into db from maplab format.")
    if args.format == "lanemap":
        if args.mode == "to_db":
            print("INFO: Load data from Lanemap format into database...")
            lanemap_io.to_db(session=session,
                               input_file=args.input_file,
                               map_name=args.map_name)
    if args.format == "lidar":
        if args.mode == "to_db":
            print("INFO: Load data from Lidar format into database...")
            lidar_io.to_db(session=session,
                               input_file=args.input_file,
                               map_name=args.map_name)
    # else not neccessary using argparse
    return


if __name__ == '__main__':
    main()

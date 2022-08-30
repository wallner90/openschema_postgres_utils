import argparse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main():
    file_formats = ["openVSLAM", "maplab", "lanemap", "lidar"]
    parser = argparse.ArgumentParser(description="openSCHEMA data loader: Load and store data to postgreSQL database.")
    parser.add_argument("-m", "--mode", type=str, choices=["load", "store"], required=True, help="Use 'load' to fetch data from the database to the given format, or 'store' to push data into the database.")
    parser.add_argument("-f", "--format", type=str, choices=file_formats, required=True, help="Dataformat of the file given using '--output_file' or '--input_file' resp.")
    parser.add_argument("-c", "--db_connection", type=str, default="postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait", help="URI of the database to connect to.")
    parser.add_argument("-n", "--map_name", type=str)
    parser.add_argument("-o", "--output_file", type=str, help="Full path to output file if 'store' is chosen'.")
    parser.add_argument("-i", "--input_file", type=str, help="Full path to input file if 'load' is chosen'.")
    args = parser.parse_args()

    # Sanity checks
    if args.mode == 'load' and (args.input_file == None or not Path(args.input_file).isfile):
        print(f"Error: Loading from file {args.input_file} not possible!")
        return
    if args.mode == "store" and not Path(args.output_file).is_dir():
        print(f"Error: {args.output_file} is no valid directory!")
        return

    engine = create_engine(args.db_connection)
    Session = sessionmaker(bind=engine)
    session = Session()

    if args.format == "openVSLAM":
        if args.mode == "load":
            print("WARNING: Not implemented yet: load from openVSLAM format.")
        elif args.mode == "store":
            print("WARNING: Not implemented yet: store from openVSLAM format.")
    if args.format == "maplab":
        if args.mode == "load":
            print("WARNING: Not implemented yet: load from maplab format.")
        elif args.mode == "store":
            print("WARNING: Not implemented yet: store from maplab format.")
    if args.format == "lanemap":
        if args.mode == "load":
            print("WARNING: Not implemented yet: load from lanemap format.")
        elif args.mode == "store":
            print("WARNING: Not implemented yet: store from lanemap format.")
    if args.format == "lidar":
        if args.mode == "load":
            print("WARNING: Not implemented yet: load from lidar format.")
        elif args.mode == "store":
            print("WARNING: Not implemented yet: store from lidar format.")



if __name__ == '__main__':
    main()
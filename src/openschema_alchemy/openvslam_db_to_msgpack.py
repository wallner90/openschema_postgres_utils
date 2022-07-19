import msgpack

from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import CreateSchema

from geoalchemy2 import Geometry, func

from sqlalchemy.orm import sessionmaker

from openschema_alchemy.model import *
from datetime import datetime
from pathlib import Path

msg_pack_file_path = Path(
    "/workspaces/openschema_postgres_utils/data/repacked.msg")

engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait', echo=False)

Session = sessionmaker(bind=engine)
session = Session()
edges = session.query(BetweenEdge).filter(BetweenEdge.edge_info.isnot(None))

for edge in edges:
    print(str(edge))

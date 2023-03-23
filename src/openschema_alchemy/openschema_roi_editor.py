# img_viewer.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from rasterio.io import MemoryFile
from rasterio.plot import show

from sqlalchemy.dialects.postgresql import JSON

from model import *

import matplotlib
matplotlib.use('TkAgg')


def main():
    engine = create_engine(
        "postgresql://postgres:postgres@localhost:5432/postgres_alchemy_ait")
    Session = sessionmaker(bind=engine)
    session = Session()

    piles = {}
    for obj in session.query(Landmark).filter(text("descriptor->>'type' = 'pile'")).all():
        piles.setdefault(obj.descriptor['pile_nr'], []).append(obj)

    connections = []
    sem_geoms = []
    
    for nr, pile in piles.items():
        # sem_geom = SemanticPolygon(description = {'type': 'pile', 'pile_nr': nr, 'description': 'A pile in in Asten.'})
        sem_geom = SemanticPolygon(type=SemanticGeometryType.Polygon.value, description = {'type': 'pile', 'pile_nr': nr, 'description': 'A pile in in Asten.'})
        sem_geoms.append(sem_geom)
        for lm in pile:
            connection = ManyLandmarkHasManySemanticGeometry(
                landmark = lm,
                order_idx = lm.descriptor['corner_id']
            )
            sem_geom.landmarks.append(connection)
            connections.append(connection)
            print("test")
        # create semantic geometry
    
    session.add_all(connections + sem_geoms)
    session.commit()


    print("test")

    # query = "SET postgis.gdal_enabled_drivers = 'ENABLE_ALL'; SELECT ST_AsGDALRaster(rast, 'GTiff') FROM ortho_raster_indexed;"

    # result = session.execute(text(query))

    # with MemoryFile(result.fetchall()[0][0].tobytes()) as memfile:
    #     ds = memfile.open()
    #     show(ds)
    #     print("Test")
    # # with rasterio.open(result[0]) as src:
    # #     raster_data = src.read(1)
    # #     rasterio.plot.show(raster_data)

    # session.close_all()


if __name__ == '__main__':
    main()

# img_viewer.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from rasterio.io import MemoryFile
from rasterio.plot import show

from datetime import datetime

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
        if not obj.semantic_geometries: piles.setdefault(obj.descriptor['pile_nr'], []).append(obj)

    ts = datetime.utcnow()
    map = Map(name='sem_polygon_map_2',
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
            kps.append(SemanticKeypoint(observation = semantic_observation, landmark = lm))
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

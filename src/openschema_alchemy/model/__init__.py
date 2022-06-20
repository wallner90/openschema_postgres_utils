from turtle import back
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import CheckConstraint, Column, ForeignKey, String, UniqueConstraint, text, ARRAY
from geoalchemy2 import Geometry

from sqlalchemy.dialects.postgresql import UUID, array, DOUBLE_PRECISION
import uuid

Base = declarative_base()


# Currently no direct implemented way for postgres inherits.
# https://docs.sqlalchemy.org/en/14/orm/inheritance.html#joined-table-inheritance

class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    topic = Column(String, unique=True)
    description = Column(String)
    type = Column(String(16))
    posegraph_id = Column(UUID(as_uuid=True), ForeignKey('posegraph.id'))

    __mapper_args__ = {
        "polymorphic_identity": "sensor",
        "polymorphic_on": type,
    }


class IMU(Sensor):
    __tablename__ = "imu"
    id = Column(UUID(as_uuid=True), ForeignKey("sensor.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "imu"
    }


class Camera(Sensor):
    __tablename__ = "camera"
    id = Column(UUID(as_uuid=True), ForeignKey("sensor.id"), primary_key=True)
    camera_rig_id = Column(UUID(as_uuid=True), ForeignKey('camera_rig.id'))

    __mapper_args__ = {
        "polymorphic_identity": "camera"
    }


class CameraRig(Base):
    __tablename__ = 'camera_rig'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    description = Column(String, unique=True)
    cameras = relationship("Camera", backref='camera_rig')


class PoseGraph(Base):
    __tablename__ = "posegraph"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    description = Column(String, unique=True)

    sensors = relationship("Sensor", backref='posegraph')
    vertices = relationship("Vertex", backref='posegraph')

class Vertex(Base):
    __tablename__ = "vertex"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    position = Column(Geometry('POINTZ'))
    posegraph_id = Column(UUID(as_uuid=True), ForeignKey('posegraph.id'))
    __table_args__ = (
        UniqueConstraint('position', 'posegraph_id',
                         name="unique_vertex_posegraph"),
    )

class Edge(Base):
    __tablename__ = "edge"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    T_A_B = Column(ARRAY(DOUBLE_PRECISION, dimensions=1),
                   server_default=array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    from_vertex_id = Column(UUID(as_uuid=True), ForeignKey('vertex.id'))
    to_vertex_id = Column(UUID(as_uuid=True), ForeignKey('vertex.id'))

    __table_args__ = (
        CheckConstraint("from_vertex_id != to_vertex_id", name="no_loop_edge"),
        UniqueConstraint('from_vertex_id', 'to_vertex_id', name="unique_edge")
    )

    from_vertex = relationship('Vertex', foreign_keys=[from_vertex_id], backref='from_vertex')
    to_vertex = relationship('Vertex', foreign_keys=[to_vertex_id], backref='to_vertex')

# TODO: Check backref and lazy stuff

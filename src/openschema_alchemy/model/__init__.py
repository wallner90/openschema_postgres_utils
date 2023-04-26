import enum
from sqlalchemy import Boolean, Enum, Integer, PrimaryKeyConstraint, Table, ForeignKeyConstraint, CheckConstraint, Column, ForeignKey, String, UniqueConstraint, text, ARRAY, JSON
from sqlalchemy.orm import declarative_base, relationship, reconstructor
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from geoalchemy2 import Geometry


Base = declarative_base(name="OpenSchema")

# TODO: maybe mixins for shared common attributes
# TODO: maybe views for inheritance     

# @declarative_mixin
# class HasUnderScoreTablename:
#     @declared_attr
#     def __tablename__(cls):
#         return "".join([f"_{c.lower()}" if c.isupper() and i > 0 else c for i, c in enumerate(cls.__name__)])

# @declarative_mixin
# class HasSensorTypeTableName:
#     @declared_attr
#     def __tablename__(cls):
#         return str(cls.__mapper_args__["polymorphic_identity"])


# @declarative_mixin
# class HasUUIDMixin:
#      @declared_attr
#      def id(cls):
#         return Column(UUID(as_uuid=True), primary_key=True,
#                server_default=text("uuid_generate_v4()"))

class SensorType(enum.Enum):
    Sensor = "sensor"
    Camera = "camera"
    IMU = "imu"
    # TODO: maybe generic PCL sensor (instead)?
    LIDAR = "lidar"
    RADAR = "radar"
    GNSS = "gnss"
    Pose = "generic_pose"
    ODOM = "generic_odom"


class Sensor(Base):
    __tablename__ = SensorType.Sensor.value
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    name = Column(String, nullable=False)
    description = Column(JSON)
    type = Column(Enum(SensorType),
                  comment="Type of sensor (e.g., camera, imu, lidar).", nullable=False)
    sensor_rig_id = Column(UUID(as_uuid=True), ForeignKey("sensor_rig.id"))

    __mapper_args__ = {
        "polymorphic_identity": SensorType.Sensor,
        "polymorphic_on": type,
    }

    __table_args__ = (
        CheckConstraint(f"type != '{SensorType.Sensor.name}'", name="sensor_is_abstract"),
        {"comment": "A generic sensor, defined by the type (e.g., camera, imu, lidar)."},
    )


class Camera(Sensor):
    __tablename__ = SensorType.Camera.value
    id = Column(UUID(as_uuid=True), ForeignKey(
        "sensor.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": SensorType.Camera,
    }


class IMU(Sensor):
    __tablename__ = SensorType.IMU.value
    id = Column(UUID(as_uuid=True), ForeignKey(
        "sensor.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": SensorType.IMU,
    }


class LIDAR(Sensor):
    __tablename__ = SensorType.LIDAR.value
    id = Column(UUID(as_uuid=True), ForeignKey(
        "sensor.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": SensorType.LIDAR,
    }


class SensorRig(Base):
    __tablename__ = "sensor_rig"
    __table_args__ = {
        "comment": "Composition of multiple sensors used."
    }
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    name = Column(String, nullable=False)
    description = Column(JSON,
                         comment="Information like extrinsics of the sensor components.")
    posegraph_id = Column(UUID(as_uuid=True), ForeignKey("posegraph.id"))

    sensors = relationship("Sensor", backref="sensor_rig")
    __table_args__ = (
        UniqueConstraint("posegraph_id", "name",
                         name="unique_sensor_per_posegraph"),
    )


class Map(Base):
    __tablename__ = "map"
    __table_args__ = {
        "comment": " "
    }
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    name = Column(String, unique=True, nullable=False)
    description = Column(JSON)
    created_at = Column(TIMESTAMP(precision=6), nullable=False)
    updated_at = Column(TIMESTAMP(precision=6), nullable=False)
    valid_until = Column(TIMESTAMP(precision=6))

    posegraphs = relationship("PoseGraph", backref="map")

    __table_args__ = (
        CheckConstraint("updated_at >= created_at ", name="map_must_be_created_before_updated"),
        CheckConstraint("valid_until IS NULL OR valid_until >= updated_at", name="map_must_be_valid_after_create")
    )


class PoseGraph(Base):
    __tablename__ = "posegraph"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    name = Column(String, nullable=False)
    description = Column(JSON)
    map_id = Column(UUID(as_uuid=True), ForeignKey("map.id"))

    root_pose = relationship("Pose", primaryjoin="and_(PoseGraph.id==Pose.posegraph_id, "
                                                 "Pose.parent_pose_id==null())", viewonly=True)
    poses = relationship("Pose", backref="posegraph")
    sensor_rig = relationship("SensorRig", backref="posegraph")


# TODO: we can add more info if relevant like acceleration and velocities (lin,ang)
class Pose(Base):
    __tablename__ = "pose"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    position = Column(Geometry("POINTZ"),
                      comment="Absolute (map) position of a pose.")
    rotation_vector = Column(Geometry("POINTZ"),
                             comment="Absolute orientation as rotation vector in the map frame.")
    uncertainty_model = Column(String,
                               comment="Type of uncertainty model in uncertainty JSON blob, not used if null.")
    uncertainty = Column(JSON,
                         comment="Uncertainty parameters for model (e.g., covariance for gaussian).")
    parent_pose_id = Column(UUID(as_uuid=True), ForeignKey("pose.id"))
    posegraph_id = Column(UUID(as_uuid=True), ForeignKey("posegraph.id"), nullable=False)

    parent = relationship("Pose", backref="children", remote_side=[id])
    observations = relationship("Observation", backref="pose")


class ObservationType(enum.Enum):
    Observation = "observation"
    Camera = SensorType.Camera.value
    IMU = SensorType.IMU.value
    LIDAR = SensorType.LIDAR.value
    RADAR = SensorType.RADAR.value
    GNSS = SensorType.GNSS.value
    Pose = SensorType.Pose.value
    # can be from an odometer or measured virtual from VO.
    ODOM = SensorType.ODOM.value
    Semantic = "semantic"


def observation_to_sensor_type(type: ObservationType) -> str:
    if type == ObservationType.Semantic:
        return 'Sensor'
    else:
        return type.name


def observation_table_name(type: ObservationType) -> str:
    return f"{type.value}_{ObservationType.Observation.value}"


class Observation(Base):
    __tablename__ = ObservationType.Observation.value
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    # Allowing this redundancy will allow us to use relationship and also constraining the sensor
    # type via the specific joined inherit table.
    # TODO: check if a view were better (at least as long it is no foreign key, does not work with views).
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensor.id"))
    pose_id = Column(UUID(as_uuid=True), ForeignKey("pose.id"))
    type = Column(Enum(ObservationType))
    created_at = Column(TIMESTAMP(precision=6), nullable=False)
    updated_at = Column(TIMESTAMP(precision=6), nullable=False)

    algorithm = Column(String)
    algorithm_settings = Column(
        JSON, comment="Algorithm specific settings depends on actual data and observation type, "
            "e.g., scale levels, thresholds, BoW description, filter settings, semantic flags, etc.")

    sensor = relationship("Sensor", backref="observations")

    __mapper_args__ = {
        "polymorphic_identity": ObservationType.Observation,
        "polymorphic_on": type,
    }

    __table_args__ = (
        # {"comment": "Represents a (preintegrated) measurement or unary factor." },
        UniqueConstraint("id", "sensor_id", name="observation_sensor_is_unique"),
        CheckConstraint("updated_at >= created_at ", name="map_must_be_created_before_updated"),
        CheckConstraint(f"type != '{ObservationType.Observation.name}'", name="observation_is_abstract"),
    )


class CameraObservation(Observation):
    __tablename__ = observation_table_name(ObservationType.Camera)
    id = Column(UUID(as_uuid=True),  ForeignKey(
        "observation.id"), primary_key=True)
    camera_sensor_id = Column(UUID(as_uuid=True), ForeignKey("camera.id"), nullable=False)

    camera = relationship("Camera", backref="camera_observations")

    __mapper_args__ = {
        "polymorphic_identity": ObservationType.Camera,
        "inherit_condition": Observation.id == id
    }

    __table_args__ = (
        ForeignKeyConstraint([id, camera_sensor_id], [Observation.id, Observation.sensor_id]),
    )


class LIDARObservation(Observation):
    __tablename__ = observation_table_name(ObservationType.LIDAR)
    id = Column(UUID(as_uuid=True),  ForeignKey(
        "observation.id"), primary_key=True)
    lidar_sensor_id = Column(UUID(as_uuid=True), ForeignKey("lidar.id"), nullable=False)
    #sensor_id = Column(UUID(as_uuid=True), ForeignKey("lidar.id"), nullable=False)
    # algorithm = Column(String)
    # algorithm_settings = Column(
    #     JSON, comment="Algorithm specific settings, e.g., scale levels, thresholds, etc.")
    # __table_args__ = (
    #     ## TODO: Check constrain: sensor needs to be a lidar
    #     CheckConstraint("sensor != to_vertex_id", name="no_loop_edge"),
    # )

    # TODO: Discuss how to store lidar observations / points for map

    lidar = relationship("LIDAR", backref="lidar_observations")
    __mapper_args__ = {
        "polymorphic_identity":  ObservationType.LIDAR,
        "inherit_condition": Observation.id == id
    }
    __table_args__ = (
        ForeignKeyConstraint([id, lidar_sensor_id], [Observation.id, Observation.sensor_id]),
    )


class SemanticObservation(Observation):
    __tablename__ = observation_table_name(ObservationType.Semantic)
    id = Column(UUID(as_uuid=True), ForeignKey(
        "observation.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity":  ObservationType.Semantic
    }


class IMUObservation(Observation):
    __tablename__ = observation_table_name(ObservationType.IMU)
    id = Column(UUID(as_uuid=True), ForeignKey(
        "observation.id"), primary_key=True)
    imu_sensor_id = Column(UUID(as_uuid=True), ForeignKey("imu.id"), nullable=False)
    data = Column(
        JSON, comment="E.g., single sample, multiple samples, or integrated pose delta.")

    imu = relationship("IMU", backref="imu_observations")
    __mapper_args__ = {
        "polymorphic_identity":  ObservationType.IMU,
        "inherit_condition": Observation.id == id
    }

    __table_args__ = (
        ForeignKeyConstraint([id, imu_sensor_id], [Observation.id, Observation.sensor_id]),
    )


class ObservationEdgeType(enum.Enum):
    # Abstract base edge
    Edge = "abstract"
    # A generic unary base edge (add extra data to an observation)
    # A single observation will probalby have 0 to 1 unary edge
    Unary = "unary"
    # A generic relative pose edge.
    # An observation could be associated with 0 to n other obervations relatively
    Between = "between"


def edge_table_name(type: ObservationEdgeType) -> str:
    return f"{type.value}_edge"


class Edge(Base):
    __tablename__ = edge_table_name(ObservationEdgeType.Edge)
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    type = Column(Enum(ObservationEdgeType))

    uncertainty_model = Column(String,
                               comment="Type of uncertainty model in uncertainty JSON blob, not used if null.")
    uncertainty = Column(JSON,  
                         comment="Uncertainty parameters for model (e.g., covariance for gaussian, erros, ...).")

    __mapper_args__ = {
        "polymorphic_identity": ObservationEdgeType.Edge,
        "polymorphic_on": type,
    }

    __table_args__ = (
        CheckConstraint(f"type != '{ObservationEdgeType.Edge.name}'", name="edge_is_abstract"),
    )


# TODO: We could implement n-ary associations via extra edge table (so that the associated ids are flexible)
#       e.g., edge id, observation-id as array or an order idx. If we do not want specializations then
#       a JSON blob would capture any data.
class UnaryEdge(Edge):
    __tablename__ = edge_table_name(ObservationEdgeType.Unary)
    id = Column(UUID(as_uuid=True), ForeignKey(edge_table_name(ObservationEdgeType.Edge)+".id"), primary_key=True)
    observation_id = Column(UUID(as_uuid=True),  ForeignKey(
        "observation.id"), nullable=False)

    position = Column(Geometry("POINTZ"),
                      comment="Position off associated pose")
    rotation_vector = Column(Geometry("POINTZ"),
                           comment="Orientation (rotational component)")

    __mapper_args__ = {
        "polymorphic_identity": ObservationEdgeType.Unary,
    }


class BetweenEdge(Edge):
    """Implements a relative pose between two other pose observations.

    For direct measurement modalities this is similar to odometry (e.g., visual odometry).
    For cameras based on their two observation keypoints allowing to reconstruct smart factors which.
    incorporate the reporojection error into graph instead of just the relative pose change based on a VO observation.

    Note that relative positions, if used, are results of the optimization. Measurements reside
    as an observation even for visually derived results (e.g., VO, semantics). They need not necessarily be the same
    as the relative pose change
    """
    __tablename__ = edge_table_name(ObservationEdgeType.Between)
    id = Column(UUID(as_uuid=True), ForeignKey(edge_table_name(ObservationEdgeType.Edge)+".id"), primary_key=True)
    from_observation_id = Column(UUID(as_uuid=True),  ForeignKey(
        "observation.id"), nullable=False)
    to_observation_id = Column(UUID(as_uuid=True),  ForeignKey(
        "observation.id"), nullable=False)
    rel_position = Column(Geometry("POINTZ"),
                      comment="Relative position change off associated pose")
    rel_rotation_vector = Column(Geometry("POINTZ"),
                           comment="Relative orientation change (rotational component)")
    edge_info = Column(JSON, comment="Additional information, e.g., is loop edge")

    __mapper_args__ = {
        "polymorphic_identity": ObservationEdgeType.Between,
    }

class KeypointType(enum.Enum):
    Keypoint = "keypoint"
    Camera = "camera_keypoint"
    LIDAR = "lidar_keypoint"
    Semantic = "semantic_keypoint"

def keypoint_table_name(type: KeypointType) -> str:
    return f"{type.value}"

class Keypoint(Base):
    __tablename__ = KeypointType.Keypoint.value
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    observation_id = Column(
        UUID(as_uuid=True), ForeignKey("observation.id"))
    point = Column(Geometry("POINT"))
    descriptor = Column(
        JSON, comment="Descriptor (algorithm specific) with needed extra info (e.g., disparity, octave, depth, angle, semantics,...).")
    landmark_id = Column(UUID(as_uuid=True), ForeignKey("landmark.id"))

    landmark = relationship('Landmark', backref='keypoints')
    observation = relationship('Observation', backref='keypoints')

    type = Column(Enum(KeypointType))

    __mapper_args__ = {
        "polymorphic_identity": KeypointType.Keypoint,
        "polymorphic_on": type,
    }

    __table_args__ = (
        CheckConstraint(f"type != '{KeypointType.Keypoint.name}'", name="keypoint_is_abstract"),
    )


class CameraKeypoint(Keypoint):
    __tablename__ = keypoint_table_name(KeypointType.Camera)
    id = Column(UUID(as_uuid=True), ForeignKey("keypoint.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity":  KeypointType.Camera
    }

class LIDARKeypoint(Keypoint):
    __tablename__ = keypoint_table_name(KeypointType.LIDAR)
    id = Column(UUID(as_uuid=True), ForeignKey("keypoint.id"), primary_key=True)

    # lidar_observation = relationship('LIDARObservation', backref='lidar_keypoints')

    __mapper_args__ = {
        "polymorphic_identity":  KeypointType.LIDAR
    }

class SemanticKeypoint(Keypoint):
    __tablename__ = keypoint_table_name(KeypointType.Semantic)
    id = Column(UUID(as_uuid=True), ForeignKey("keypoint.id"), primary_key=True)

    # semantic_observation = relationship('SemanticObservation', backref='semantic_keypoints')
    __mapper_args__ = {
        "polymorphic_identity":  KeypointType.Semantic
    }

# A manual/virtual landmark may be attached to another observed landmark or it may be have it's own observation
# relatively attached to a pose via the semantic keypoint or the landmark just exists independently
# (no optimization possible)
class Landmark(Base):
    __tablename__ = "landmark"
    __table_args__ = {
        "comment": "A 3D (or  6DoF) point in the map serving as basis \
            for all map elements (part of observation and building up \
                semantic geometric elements."
    }
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    position = Column(Geometry("POINTZ"))
    rotation_vector = Column(Geometry("POINTZ"),
                           comment="Absolute orientation as rotation vector in the map frame (at position); null if not used.")
    uncertainty_model = Column(String,
                               comment="Type of uncertainty model in uncertainty JSON blob, not used if null.")
    uncertainty = Column(JSON,
                         comment="Uncertainty parameters for model (e.g., covariance for gaussian).")
    descriptor = Column(
        JSON, comment="Landmark specific information, e.g., semantic information (is a pallet, is on a house, is agent,, etc).")

    semantic_geometries = relationship(
        "ManyLandmarkHasManySemanticGeometry", back_populates="landmark")


class ManyLandmarkHasManySemanticGeometry(Base):
    __tablename__ = "many_landmarks_has_many_semantic_geometries"
    landmark_id = Column(ForeignKey("landmark.id"), primary_key=True)
    semantic_geometry_id = Column(ForeignKey("semantic_geometry.id"), primary_key=True)
    order_idx = Column(Integer)
    landmark = relationship("Landmark", back_populates="semantic_geometries")
    semantic_geometry = relationship("SemanticGeometry", back_populates="landmarks")


# landmark_to_semantic_geometry_association_table = Table(
#     "many_landmarks_has_many_semantic_geometries",
#     Base.metadata,
#     Column("landmark_id", ForeignKey("landmark.id")),
#     Column("semantic_geometry_id", ForeignKey("semantic_geometry.id")),
#     Column("order_idx", Integer),
#     PrimaryKeyConstraint("landmark_id", "semantic_geometry_id",
#                          name="many_landmarks_has_many_semantic_geometries_pkey"),
#     CheckConstraint(
#         "order_idx >= 0", name="many_landmarks_has_many_semantic_geometries_order_idx_positive")
# )

class SemanticGeometryType(enum.Enum):
    Geometry = "semantic_geometry"
    Linestring = "semantic_line_string"
    Polygon = "semantic_polygon"
    Object  = "semantic_object"


def geometry_table_name(type: SemanticGeometryType) -> str:
    return f"{type.value}"

class SemanticGeometry(Base):
    __tablename__ = SemanticGeometryType.Geometry.value
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    type = Column(Enum(SemanticGeometryType))
    description = Column(
        JSON, comment="Depending on type, description of geometry (e.g., linestring, lane, area, ...)")
    landmarks = relationship(
        "ManyLandmarkHasManySemanticGeometry", back_populates="semantic_geometry")

    __mapper_args__ = {
        "polymorphic_identity": SemanticGeometryType.Geometry,
        "polymorphic_on": type,
    }

class SemanticObject(SemanticGeometry):
    __tablename__ = geometry_table_name(SemanticGeometryType.Object)
    __table_args__ = (
        {"comment": "A generic geometry defining a volume by "
                    "one or multiple landmarks (sphere, box,...) "
                    "via description."},
    )
    id = Column(UUID(as_uuid=True), ForeignKey(
            "semantic_geometry.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": SemanticGeometryType.Object,
    }

class SemanticLineString(SemanticGeometry):
    __tablename__ = geometry_table_name(SemanticGeometryType.Linestring)
    id = Column(UUID(as_uuid=True), ForeignKey(
        "semantic_geometry.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity":  SemanticGeometryType.Linestring,
    }

class SemanticPolygon(SemanticGeometry):
    __tablename__ = geometry_table_name(SemanticGeometryType.Polygon)
    id = Column(UUID(as_uuid=True), ForeignKey(
        "semantic_geometry.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity":  SemanticGeometryType.Polygon,
    }

class SemanticRegulatoryElement(Base):
    __tablename__ = "semantic_regulatory_element"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    description = Column(
        JSON, comment="Defines regulatory information like one-way, speed-limit (per traffic participant type)")


class SemanticLane(Base):
    __tablename__ = "semantic_lane"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    name = Column(String, nullable=False)
    regulatory_element_id = Column(
        UUID(as_uuid=True), ForeignKey("semantic_regulatory_element.id"))
    left_line_id = Column(UUID(as_uuid=True),
                          ForeignKey("semantic_line_string.id"))
    right_line_id = Column(UUID(as_uuid=True),
                           ForeignKey("semantic_line_string.id"))
    description = Column(JSON, comment="Extra info")
    __table_args__ = (
        CheckConstraint("left_line_id != right_line_id",
                        name="semantic_lane_defined_by_distinct_lines"),
    )

class SemanticFreeDriveZone(Base):
    __tablename__ = "semantic_free_drive_zone"
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("uuid_generate_v4()"))
    name = Column(String)
    regulatory_element_id = Column(
        UUID(as_uuid=True), ForeignKey("semantic_regulatory_element.id"))
    polyon_id = Column(UUID(as_uuid=True), ForeignKey(
        "semantic_polygon.id"), nullable=False)
    description = Column(JSON, comment="Extra info")

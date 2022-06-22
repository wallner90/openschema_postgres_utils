import enum
from sqlalchemy import Enum, Integer, PrimaryKeyConstraint, Table, CheckConstraint, Column, ForeignKey, String, UniqueConstraint, text, ARRAY, JSON, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry


Base = declarative_base()


class SensorType(enum.Enum):
    Camera = 'Camera'
    IMU = 'IMU'
    LIDAR = 'LIDAR'
    RADAR = 'RADAR'
    GNSS = 'GNSS'
    GenericAbsolute = 'GenericAbsolute'


class Sensor(Base):
    __tablename__ = 'sensor'
    __table_args__ = {
        'comment': 'A generic sensor, defined by the type (e.g., camera, imu, lidar).'
    }
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String)
    description = Column(JSON)
    type = Column(Enum(SensorType),
                  comment='Type of sensor (e.g., camera, imu, lidar).')
    sensor_rig_id = Column(UUID(as_uuid=True), ForeignKey('sensor_rig.id'))

    __mapper_args__ = {
        "polymorphic_identity": 'sensor',
        "polymorphic_on": type,
    }


class Camera(Sensor):
    __tablename__ = 'camera'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "sensor.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": SensorType.Camera,
    }


class IMU(Sensor):
    __tablename__ = 'imu'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "sensor.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": SensorType.IMU,
    }


class Lidar(Sensor):
    __tablename__ = 'lidar'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "sensor.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": SensorType.LIDAR,
    }


class SensorRig(Base):
    __tablename__ = 'sensor_rig'
    __table_args__ = {
        'comment': 'Composition of multiple sensors used.'
    }
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String)
    description = Column(JSON,
                         comment='Information like extrinsics of the sensor components.')
    posegraph_id = Column(UUID(as_uuid=True), ForeignKey('posegraph.id'))

    sensors = relationship('Sensor', backref='sensor_rig')
    __table_args__ = (
        UniqueConstraint('posegraph_id', 'name',
                         name='unique_sensor_per_posegraph'),
    )


class Map(Base):
    __tablename__ = 'map'
    __table_args__ = {
        'comment': ' '
    }
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String, unique=True)
    description = Column(JSON)
    create_time = Column(TIMESTAMP)
    valid_until = Column(TIMESTAMP)


class PoseGraph(Base):
    __tablename__ = 'posegraph'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String)
    description = Column(JSON)
    map_id = Column(UUID(as_uuid=True), ForeignKey('map.id'))


class Pose(Base):
    __tablename__ = 'pose'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    position = Column(Geometry('POINTZ'),
                      comment='Absolute (map) position of a pose (with orientation as normal_vector).')
    normal_vector = Column(Geometry('POINTZ'),
                           comment='Absolute orientation as normal vector in the map frame (at position).')
    uncertainty_model = Column(String,
                               comment='Type of uncertainty model in uncertainty JSON blob, not used if null.')
    uncertainty = Column(JSON,
                         comment='Uncertainty parameters for model (e.g., covariance for gaussian).')
    parent_pose_id = Column(
        UUID(as_uuid=True), ForeignKey('pose.id'), nullable=True)
    posegraph_id = Column(UUID(as_uuid=True), ForeignKey('posegraph.id'))


class ObservationType(enum.Enum):
    Camera = str(SensorType.Camera)
    IMU = str(SensorType.IMU)
    LIDAR = str(SensorType.LIDAR)
    RADAR = str(SensorType.RADAR)
    GNSS = str(SensorType.GNSS)
    GenericAbsolute = str(SensorType.GenericAbsolute)
    Semantic = 'Semantic'


class Observation(Base):
    __tablename__ = 'observation'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    pose_id = Column(UUID(as_uuid=True), ForeignKey('pose.id'))
    type = Column(Enum(ObservationType))
    create_time = Column(TIMESTAMP)
    updated_time = Column(TIMESTAMP)

    __mapper_args__ = {
        "polymorphic_identity": "observation",
        "polymorphic_on": type,
    }


class CameraObservation(Observation):
    __tablename__ = 'camera_observation'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "observation.id"), primary_key=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey('camera.id'))
    algorithm = Column(String)
    algorithm_settings = Column(
        JSON, comment='Algorithm specific settings, e.g., scale levels, thresholds, BoW description, etc.')
    # __table_args__ = (
    #     ## TODO: Check constrain: sensor needs to be a camera
    #     CheckConstraint('sensor != to_vertex_id', name='no_loop_edge'),
    # )
    __mapper_args__ = {
        "polymorphic_identity": "camera_observation"
    }

    # __table_args__ = (
    #     ## TODO: Check constrain: Sensor_id must exist in post_graph's sensor rig
    #     CheckConstraint("sensor.type == 'Camera'", name='test_constraint'),
    # )


class LidarObservation(Observation):
    __tablename__ = 'lidar_observation'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "observation.id"), primary_key=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey('lidar.id'))
    # algorithm = Column(String)
    # algorithm_settings = Column(
    #     JSON, comment='Algorithm specific settings, e.g., scale levels, thresholds, etc.')
    # __table_args__ = (
    #     ## TODO: Check constrain: sensor needs to be a lidar
    #     CheckConstraint('sensor != to_vertex_id', name='no_loop_edge'),
    # )

    # TODO: Discuss how to store lidar observations / points for map

    __mapper_args__ = {
        "polymorphic_identity": "lidar_observation"
    }


class SemanticObservation(Observation):
    __tablename__ = 'semantic_observation'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "observation.id"), primary_key=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey(
        'sensor.id'), comment='Null if manual entry and not derived from sensor data.')
    algorithm = Column(String)
    algorithm_settings = Column(
        JSON, comment='Algorithm specific settings for data interpretation.')
    # __table_args__ = (
    #     ## TODO: Check constrain: sensor needs to be a lidar
    #     CheckConstraint('sensor != to_vertex_id', name='no_loop_edge'),
    # )

    __mapper_args__ = {
        "polymorphic_identity": "semantic_observation"
    }


class IMUObservation(Observation):
    __tablename__ = 'imu_observation'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "observation.id"), primary_key=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey('imu.id'))
    algorithm = Column(String)
    algorithm_settings = Column(
        JSON, comment='E.g., filter settings, integration options, etc.')
    data = Column(
        JSON, comment='E.g., single sample, multiple samples, or integrated pose delta.')
    # __table_args__ = (
    #     ## TODO: Check constrain: sensor needs to be a lidar
    #     CheckConstraint('sensor != to_vertex_id', name='no_loop_edge'),
    # )

    __mapper_args__ = {
        "polymorphic_identity": "imu_observation"
    }


class CameraKeypoint(Base):
    __tablename__ = 'camera_keypoint'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    camera_observation_id = Column(
        UUID(as_uuid=True), ForeignKey('camera_observation.id'))
    point = Column(Geometry('POINT'))
    descriptor = Column(
        JSON, comment='Descriptor (algorithm specific) with needed extra info (e.g., disparity, octave, depth, angle, semantics,...).')
    landmark_id = Column(UUID(as_uuid=True), ForeignKey('landmark.id'))


class LidarKeypoint(Base):
    __tablename__ = 'lidar_keypoint'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    lidar_observation_id = Column(
        UUID(as_uuid=True), ForeignKey('lidar_observation.id'))
    point = Column(Geometry(
        'POINTZ'), comment="Sensor reading in sensor coordinate frame; null if not used.")
    descriptor = Column(
        JSON, comment='Descriptor (sensor specific), e.g. RSSI, semantics, etc..')
    landmark_id = Column(UUID(as_uuid=True), ForeignKey('landmark.id'))


class SemanticKeypoint(Base):
    __tablename__ = 'semantic_keypoint'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    semantic_observation_id = Column(
        UUID(as_uuid=True), ForeignKey('semantic_observation.id'))
    point = Column(Geometry('POINTZ'),
                   comment="Observation in sensor frame; null if manual entry.")
    descriptor = Column(
        JSON, comment='Descriptor (algorithm / detctor specific), e.g. class (Palette, House, Agent, ...), stability, etc..')
    landmark_id = Column(UUID(as_uuid=True), ForeignKey('landmark.id'))

# A manual/virtual landmark (e.g. could be not part of the optimization or not generated)


class Landmark(Base):
    __tablename__ = 'landmark'
    __table_args__ = {
        'comment': 'A 3D (or  6DoF) point in the map serving as basis \
            for all map elements (part of observation and building up \
                semantic geometric elements.'
    }
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    position = Column(Geometry('POINTZ'))
    normal_vector = Column(Geometry('POINTZ'),
                           comment='Absolute orientation as normal vector in the map frame (at position); null if not used.')
    uncertainty_model = Column(String,
                               comment='Type of uncertainty model in uncertainty JSON blob, not used if null.')
    uncertainty = Column(JSON,
                         comment='Uncertainty parameters for model (e.g., covariance for gaussian).')
    descriptor = Column(
        JSON, comment='Landmark specific information, e.g., semantic information (is a pallet, is on a house, is agent,, etc).')


landmark_to_semantic_geometry_association_table = Table(
    "many_landmarks_has_many_semantic_geometries",
    Base.metadata,
    Column('landmark_id', ForeignKey('landmark.id')),
    Column('semantic_geometry_id', ForeignKey('semantic_geometry.id')),
    Column('order_idx', Integer),
    PrimaryKeyConstraint('landmark_id', 'semantic_geometry_id',
                         name="many_landmarks_has_many_semantic_geometries_pkey"),
    CheckConstraint(
        'order_idx >= 0', name="many_landmarks_has_many_semantic_geometries_order_idx_positive")
)


class SemanticGeometry(Base):
    __tablename__ = 'semantic_geometry'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    type = Column(String)
    description = Column(
        JSON, comment='Depending on type, description of geometry (e.g., linestring, lane, area, ...)')
    landmarks = relationship(
        "Landmark", secondary=landmark_to_semantic_geometry_association_table)

    __mapper_args__ = {
        "polymorphic_identity": "semantic_geometry",
        "polymorphic_on": type,
    }


class SemanticLineString(SemanticGeometry):
    __tablename__ = 'semantic_line_string'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "semantic_geometry.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "semantic_line_string"
    }


class SemanticPolygon(SemanticGeometry):
    __tablename__ = 'semantic_polygon'
    id = Column(UUID(as_uuid=True), ForeignKey(
        "semantic_geometry.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "semantic_polygon"
    }


class SemanticRegulatoryElement(Base):
    __tablename__ = 'semantic_regulatory_element'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    description = Column(
        JSON, comment='Defines regulatory information like one-way, speed-limit (per traffic participant type)')


class SemanticLane(Base):
    __tablename__ = 'semantic_lane'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String)
    regulatory_element_id = Column(
        UUID(as_uuid=True), ForeignKey('semantic_regulatory_element.id'))
    left_line_id = Column(UUID(as_uuid=True),
                          ForeignKey('semantic_line_string.id'))
    right_line_id = Column(UUID(as_uuid=True),
                           ForeignKey('semantic_line_string.id'))
    description = Column(JSON, comment='Extra info')
    __table_args__ = (
        CheckConstraint('left_line_id != right_line_id',
                        name='semantic_lane_defined_by_distinct_lines'),
    )


class SemanticFreeDriveZone(Base):
    __tablename__ = 'semantic_free_drive_zone'
    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String)
    regulatory_element_id = Column(
        UUID(as_uuid=True), ForeignKey('semantic_regulatory_element.id'))
    polyon_id = Column(UUID(as_uuid=True), ForeignKey(
        'semantic_polygon.id'), nullable=False)
    description = Column(JSON, comment='Extra info')

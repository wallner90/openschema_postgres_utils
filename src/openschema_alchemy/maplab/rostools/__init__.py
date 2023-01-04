import rospy

from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header

rospy.init_node('maplab_rostools')


class PointCloudPublisher:
    def __init__(self, pointcloud_topic: str):
        self._publisher = rospy.Publisher(pointcloud_topic, PointCloud2, queue_size=100)
        self._point_cloud = None

    def publish(self, points):
        header = Header()
        header.stamp = rospy.Time.now()
        header.frame_id = "map"
        point_cloud = point_cloud2.create_cloud_xyz32(header, points)
        self._publisher.publish(point_cloud)

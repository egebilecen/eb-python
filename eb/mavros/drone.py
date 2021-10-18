import rospy
from mavros_msgs.msg   import State, GlobalPositionTarget
from sensor_msgs.msg   import NavSatFix
from std_msgs.msg      import Float64
from geometry_msgs.msg import PoseStamped

from mavros_msgs.srv import SetMode, CommandBool, CommandTOL

class MAVROS_Drone:
    def __init__(self):
        # Subscribers
        self.sub_state                  = rospy.Subscriber("/mavros/state",                        State,     self.cb_state)
        self.sub_global_position_global = rospy.Subscriber("/mavros/global_position/global",       NavSatFix, self.cb_global_position_global)
        self.sub_global_position_global = rospy.Subscriber("/mavros/global_position/rel_alt",      Float64,   self.cb_global_position_rel_alt)
        self.sub_global_position_global = rospy.Subscriber("/mavros/global_position/compass_hdg", Float64,   self.cb_global_position_compass_hdg)

        # Publishers
        self.pub_setpoint_position_global = rospy.Publisher("/mavros/setpoint_position/global", GlobalPositionTarget, queue_size=10)
        self.pub_setpoint_position_local  = rospy.Publisher("/mavros/setpoint_position/local",  PoseStamped,          queue_size=10)

        # Services
        self.srv_set_mode    = rospy.ServiceProxy("/mavros/set_mode",    SetMode)
        self.srv_cmd_arming  = rospy.ServiceProxy("/mavros/cmd/arming",  CommandBool)
        self.srv_cmd_takeoff = rospy.ServiceProxy("/mavros/cmd/takeoff", CommandTOL)
        self.srv_cmd_land    = rospy.ServiceProxy("/mavros/cmd/land",    CommandTOL)

        # Variables
        self._state      = None
        self._global_pos = None
        self._rel_alt    = None
        self._heading    = None

    # Functions
    def set_flight_mode(self, mode="GUIDED"):
        return self.srv_set_mode(0, mode.upper())

    def arm(self):
        return self.srv_cmd_arming(True)

    def disarm(self):
        return self.srv_cmd_arming(False)

    def takeoff(self, alt=2): # Not tested
        return self.srv_cmd_takeoff(0, 0, 0, 0, alt)

    def land(self): # Not tested
        return self.srv_cmd_land(0, 0, 0, 0, 0)

    def get_state(self):
        return self._state

    def get_global_pos(self):
        return self._global_pos

    def get_relative_alt(self):
        return self._rel_alt

    def get_heading(self):
        return self._heading

    def go_to_global_pos(self, lat, lon, alt=10):
        global_pos_target = GlobalPositionTarget()

        global_pos_target.coordinate_frame = 6 # FRAME_GLOBAL_REL_ALT
        global_pos_target.type_mask = 0b0000111111111000

        global_pos_target.latitude  = lat
        global_pos_target.longitude = lon
        global_pos_target.altitude  = alt

        global_pos_target.velocity.x = 0
        global_pos_target.velocity.y = 0
        global_pos_target.velocity.z = 0

        global_pos_target.acceleration_or_force.x = 0
        global_pos_target.acceleration_or_force.y = 0
        global_pos_target.acceleration_or_force.z = 0

        global_pos_target.yaw = 0
        global_pos_target.yaw_rate = 0

        self.pub_setpoint_position_global.publish(global_pos_target)

    def move_based_local_ned(self, vel_x, vel_y, vel_z):
        ned_data = PoseStamped()

        ned_data.pose.position.x = vel_x
        ned_data.pose.position.y = vel_y
        ned_data.pose.position.z = vel_z

        ned_data.pose.orientation.x = 0
        ned_data.pose.orientation.y = 0
        ned_data.pose.orientation.z = 0

        self.pub_setpoint_position_local.publish(ned_data)

    # Callbacks
    def cb_state(self, data):
        self._state = data

    def cb_global_position_global(self, data):
        self._global_pos = data

    def cb_global_position_rel_alt(self, data):
        self._rel_alt = data.data

    def cb_global_position_compass_hdg(self, data):
        self._heading = data.data

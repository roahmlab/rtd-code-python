from rtd.entity.components import BaseInfoComponent
from rtd.entity.states import ArmRobotState
from rtd.util.mixins import Options
from copy import deepcopy
from urchin import URDF
import numpy as np
from nptyping import NDArray, Shape, Float64

# define top level module logger
import logging
logger = logging.getLogger(__name__)

# type hinting
BoundsVec = NDArray[Shape['N,2'], Float64]



class ArmourAgentInfo(BaseInfoComponent, Options):
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "M_min_eigenvalue": 0.002,
            "gravity": [0, 0, -9,81],
            "joint_velocity_limits": None,
            "joint_torque_limits": None,
            "transmission_inertia": None,
            "buffer_dist": 0,
        }
    
    
    def __init__(self, robot, params, **options):
         # initialize base classes
        BaseInfoComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.robot: URDF = deepcopy(robot)
        self.params = params
        
        # initialzie
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        if "joint_velocity_limits" not in options:
            raise Exception("Must pass in joint_velocity_limits externally!")
        if "joint_torque_limits" not in options:
            raise Exception("Must pass in joint_torque_limits externally!")
        
        # fill in other dependent factors
        self.robot.Gravity = options["gravity"]
        self.n_links_and_joints = self.params.nomianal.num_joints
        self.num_q = self.params.nominal.num_q
        self.body_joint_index = self.params.nominal.q_index
        
        # flesh out the links of the robot
        
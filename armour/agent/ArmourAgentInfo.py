from rtd.entity.components import BaseInfoComponent
from rtd.entity.states import ArmRobotState
from rtd.util.mixins import Options
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
            "transmission_inertia": None,
            "buffer_dist": 0,
        }
    
    
    def __init__(self, robot: URDF, params, **options):
         # initialize base classes
        BaseInfoComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.robot: URDF = robot.copy()
        self.params = params
        
        # initialzie
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)        
        # fill in other dependent factors
        self.robot.Gravity = options["gravity"]
        self.n_links_and_joints = self.params.nomianal.num_joints
        self.num_q = self.params.nominal.num_q
        self.body_joint_index = self.params.nominal.q_index
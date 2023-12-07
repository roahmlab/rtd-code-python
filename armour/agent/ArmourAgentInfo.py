from rtd.entity.components import BaseInfoComponent
from rtd.util.mixins import Options
from zonopyrobots import ZonoArmRobot
from urchin import URDF
import torch

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ArmourAgentInfo(BaseInfoComponent, Options):
    @staticmethod
    def defaultoptions() -> dict:
        '''
        Sets the default options for the ArmourAgentInfo, such
        as `M_min_eigenvalue`, `gravity`, `transmission_inertia`,
        and `buffer_dist`.
        '''
        return {
            "M_min_eigenvalue": 0.002,
            "gravity": [0, 0, -9.81],
            "transmission_inertia": None,
            "buffer_dist": 0,
            "torch_device": torch.device("cpu"),
        }
    
    
    def __init__(self, robot: URDF, **options):
         # initialize base classes
        BaseInfoComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        options = self.mergeoptions(options)

        # Save a ZonoArmRobot object generated from this URDF
        self.params = ZonoArmRobot.load(robot, device=options["torch_device"], dtype=torch.double)
        self.urdf = self.params.urdf
        
        # initialzie
        self.reset()
    
    
    def reset(self, **options):
        '''
        Resets the ArmourAgentInfo
        '''
        options = self.mergeoptions(options)        
        # fill in other dependent factors
        #self.n_links_and_joints = self.params.nomianal.num_joints
        self.n_q = self.params.dof
        #self.body_joint_index = self.params.nominal.q_index
        self.M_min_eigenvalue = options["M_min_eigenvalue"]
        self.gravity = options["gravity"]
        self.transmission_inertia = options["transmission_inertia"]
        self.buffer_dist = options["buffer_dist"]
    
    
    def __str__(self):
        return (f"Info component {repr(self)} with properties:\n" + 
                f"   n_q:  {self.n_q}\n")
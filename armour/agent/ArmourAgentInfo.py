from rtd.entity.components import BaseInfoComponent
from rtd.util.mixins import Options
from zonopy.robots2.robot import ZonoArmRobot
from urchin import URDF

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
            "gravity": [0, 0, -9,81],
            "transmission_inertia": None,
            "buffer_dist": 0,
        }
    
    
    def __init__(self, robot: URDF, params: ZonoArmRobot, **options):
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
        '''
        Resets the ArmourAgentInfo
        '''
        options = self.mergeoptions(options)        
        # fill in other dependent factors
        #self.n_links_and_joints = self.params.nomianal.num_joints
        self.n_q = len(self.robot.actuated_joints)
        #self.body_joint_index = self.params.nominal.q_index
        self.M_min_eigenvalue = options["M_min_eigenvalue"]
        self.gravity = options["gravity"]
        self.transmission_inertia = options["transmission_inertia"]
        self.buffer_dist = options["buffer_dist"]
    
    
    def __str__(self):
        return (f"Info component {repr(self)} with properties:\n" + 
                f"   n_q:  {self.n_q}\n")
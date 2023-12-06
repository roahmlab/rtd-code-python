from rtd.entity.components import BaseControllerComponent
from rtd.util.mixins import Options
from rtd.planner.trajectory import Trajectory
from rtd.entity.states import EntityState
from armour.agent import ArmourAgentInfo, ArmourAgentState
from armour.trajectory import ZeroHoldArmTrajectory
import numpy as np

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ArmourIdealController(BaseControllerComponent, Options):
    @staticmethod
    def defaultoptions() -> dict:
        return {
            'use_true_params_for_robust': False,
            'use_distribution_norm': False,
            'Kr': 10,
            'alpha_constant': 1,
            'V_max': 3.1e-7,
            'r_norm_threshold': 0,
        }
    
    
    def __init__(self, arm_info: ArmourAgentInfo, arm_state: ArmourAgentState, **options):
        # initialize base classes
        BaseControllerComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.robot_info: ArmourAgentInfo = arm_info
        self.robot_state: ArmourAgentState = arm_state
        
        # initialize
        # self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.n_inputs = self.robot_info.n_q
        self.k_r = options["Kr"]
        self.alpha_constant = options["alpha_constant"]
        self.V_max = options["V_max"]
        self.r_norm_threshold = options["r_norm_threshold"]
        
        # compute ultimate bounds
        if hasattr(self.robot_info, 'M_min_eigenvalue'):
            self.ultimate_bound = np.sqrt(2*self.V_max/self.robot_info.M_min_eigenvalue)
            self.ultimate_bound_position = (1/self.k_r) * self.ultimate_bound
            self.ultimate_bound_velocity = 2*self.ultimate_bound
            logger.info(f"Computed ultimate bound of {self.ultimate_bound:.3f}")
        else:
            self.ultimate_bound = None
            logger.warning("No minimum eigenvalue of agent mass matrix specified, can not compute ultimate bound")
        
        # create the initial trajectory
        self.trajectories.setInitialTrajectory(ZeroHoldArmTrajectory(self.robot_state.get_state()))
        self.trajectories.clear()
    
    
    def setTrajectory(self, trajectory: Trajectory):
        if trajectory.validate():
            self.trajectories.setTrajectory(trajectory)
    
    
    def getControlInputs(self, t: list[float], **options) -> EntityState:
        startTime = self.robot_state.get_state().time
        target: EntityState = self.trajectories.getCommand(startTime + t)[0]
        return target
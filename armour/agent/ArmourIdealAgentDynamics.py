from rtd.entity.components import BaseDynamicsComponent
from rtd.util.mixins import Options
from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmourController
from rtd.planner.trajectory import Trajectory
import numpy as np

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ArmourIdealAgentDynamics(BaseDynamicsComponent, Options):
    '''
    Dynamics component that assumes the agent perfectly
    executes the reference trajectory
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "time_discretization": 0.01,
        }
    
    
    def __init__(self, arm_info: ArmourAgentInfo, arm_state: ArmourAgentState, 
                 arm_controller: ArmourController, **options):
         # initialize base classes
        BaseDynamicsComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.robot_info: ArmourAgentInfo = arm_info
        self.robot_state: ArmourAgentState = arm_state
        self.controller: ArmourController = arm_controller
        
        # initialzie
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)        
        self.time_discretization = options["time_discretization"]
    
    
    def move(self, t_move: float):
        logger.info("Moving!")
        
        # get the current time and prep measurement time
        state = self.robot_state.get_state()
        tcur = state.time
        t_meas = np.arange(0, t_move, self.time_discretization)
        
        # prepare the trajectory
        trajectory: Trajectory = self.controller.trajectories[-1]
        target = trajectory.getCommand(tcur + t_meas)
        
        # we assume it just follows the trajectory perfectly
        tout = t_meas
        zout = np.zeros((state.state.shape[0], tout.size))
        zout[self.robot_state.position_indices, :] = target.position
        zout[self.robot_state.velocity_indices, :] = target.velocity
        
        # save the motion data
        self.robot_state.commit_state_data(tout, zout)
    
    
    def controller_input_check(self, t_check_step) -> bool:
        '''
        Check that the controller wasn't giving bad torques
        '''
        logger.info("Assuming perfect kinematics, skipping input torque check!")
        return False
    
    
    def __str__(self):
        return (f"Dynamics component {repr(self)} with properties:\n" + 
                f"   arm_info:  {repr(self.robot_info)}\n" +
                f"   arm_state: {repr(self.robot_state)}\n" +
                f"   arm_controller: {repr(self.controller)}\n") 
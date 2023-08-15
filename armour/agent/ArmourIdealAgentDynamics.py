from rtd.entity.components import BaseDynamicsComponent
from rtd.util.mixins import Options
from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmourMexController

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ArmourIdealAgentDynamics(BaseDynamicsComponent):
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
                 arm_controller: ArmourMexController, **options):
         # initialize base classes
        BaseDynamicsComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.arm_info: ArmourAgentInfo = arm_info
        self.arm_state: ArmourAgentState = arm_state
        self.arm_controller: ArmourMexController = arm_controller
        
        # initialzie
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)        
        self.time_discretization = options["time_discretization"]
    
    
    def move(self, t_move: float):
        pass
    
    
    def __str__(self):
        return (f"Dynamics component {repr(self)} with properties:\n" + 
                f"   arm_info:  {repr(self.arm_info)}\n" +
                f"   arm_state: {repr(self.arm_state)}\n" +
                f"   arm_controller: {repr(self.arm_controller)}\n") 
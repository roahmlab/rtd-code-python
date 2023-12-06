from abc import ABCMeta, abstractmethod
from rtd.entity.components import BaseInfoComponent, BaseStateComponent
from rtd.planner.trajectory import Trajectory



class BaseControllerComponent(metaclass=ABCMeta):
    '''
    Base class for the controller of the agent.
    Stores a reference to the info and state components, as well
    as a container for the trajectories, and the number of inputs.
    '''
    def __init__(self):
        self.robot_info: BaseInfoComponent = None
        self.robot_state: BaseStateComponent = None
        self.trajectories: list[Trajectory] = None
        self.n_inputs: int = 0
    

    @abstractmethod
    def reset(self):
        '''
        Abstract method which needs to be implemented
        to reset each property
        '''
        pass

    
    @abstractmethod
    def setTrajectory(self, trajectory: Trajectory):
        '''
        Abstract method which needs to be implemented
        to set the trajectory of the controller
        '''
        pass
    
    
    @abstractmethod
    def getControlInputs(self, **options):
        '''
        Abstract method which needs to be implemented
        to get the inputs
        '''
        pass
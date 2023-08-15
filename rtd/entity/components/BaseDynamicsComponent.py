from abc import ABCMeta, abstractmethod
from rtd.entity.components import BaseInfoComponent, BaseStateComponent



class BaseDynamicsComponent(metaclass=ABCMeta):
    '''
    Base class for controlling the dynamics of an agent
    '''
    def __init__(self):
        self.robot_info: BaseInfoComponent = None
        self.robot_state: BaseStateComponent = None
        self.controller = None
    

    @abstractmethod
    def reset(self):
        '''
        Abstract method which needs to be implemented
        to reset each property
        '''
        pass

    
    @abstractmethod
    def move(self, t_move: float):
        '''
        Abstract method which needs to be implemented
        to control the dynamics
        '''
        pass
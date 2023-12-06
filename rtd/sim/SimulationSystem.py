from abc import ABCMeta, abstractmethod
from rtd.util.mixins.Typings import Vec



class SimulationSystem(metaclass=ABCMeta):
    '''
    Base class for visual and collision systems 
    '''
    def __init__(self):
        self.time: Vec = None
        self.time_discretization: float = None
    
    
    @abstractmethod
    def reset(self):
        '''
        Abstract method which needs to be implemented
        to reset the system
        '''
        pass
from abc import ABCMeta, abstractmethod



class SimulationSystem(metaclass=ABCMeta):
    '''
    Base class for visual and collision systems 
    '''
    def __init__(self):
        self.time = None
        self.time_discretization = None
    
    
    @abstractmethod
    def reset(self):
        '''
        Abstract method which needs to be implemented
        to reset the system
        '''
        pass
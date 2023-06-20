from abc import ABCMeta, abstractmethod
from rtd.entity.components import BaseInfoComponent



class BaseStateComponent(metaclass=ABCMeta):
    '''
    Base class for storing dynamic parameters tied
    to an entity. Should be extended along with the 
    `Options` mixin to implement specific behaviors
    '''
    def __init__(self):
        # stores a copy of the entity's info
        self.entityinfo: BaseInfoComponent = None
        
        # number of states in the entity
        self.n_states: int = None
        
        # an (n_states, :) list of states at various times
        self.state: list[list] = None
        
        # a list of times corresponding to each state
        self.time: list[float] = None
    

    @abstractmethod
    def reset(self):
        '''
        Abstract method which needs to be implemented
        to reset the `state` and `time`
        '''
        pass


    @abstractmethod
    def get_state(self, time: float) -> dict:
        '''
        Abstract method which needs to be implemented.
        Returns a dict with the state at a certain time
        '''
        pass
    
    
    @abstractmethod
    def random_init(self):
        '''
        Abstract method which needs to be implemented
        to initialize the starting `state` randomly
        '''
        pass
    
    
    @abstractmethod
    def commit_state_data(self, time: float, state: list[float]):
        '''
        Abstract method which needs to be implemented
        to append a state and time to the `state` and
        `time` lists
        '''
        pass
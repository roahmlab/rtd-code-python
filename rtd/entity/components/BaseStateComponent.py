from abc import ABCMeta, abstractmethod
from rtd.entity.components import BaseInfoComponent
from rtd.util.mixins.Typings import Vec, Mat



class BaseStateComponent(metaclass=ABCMeta):
    '''
    Base class for storing dynamic parameters tied to an entity.
    Should be extended along with the `Options` mixin to implement
    specific behaviors.
    Stores a refernce to the info component, as well as the number
    of states, and the internal state and time storage.
    '''
    def __init__(self):
        # stores a copy of the entity's info
        self.entityinfo: BaseInfoComponent = None
        
        # number of states in the entity
        self.n_states: int = None
        
        # an (n_states, :) matrix of states at various times
        self.state: Mat = None
        
        # a list of times corresponding to each state
        self.time: Vec = None
    

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
        
        Parameters
        ----------
        time : float
            time to get the state at
        
        Returns
        -------
        state : dict
            dict with keys time and state, with the time the state
            was requested at, and its corresponding state
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
    def commit_state_data(self, time: float, state: Vec):
        '''
        Abstract method which needs to be implemented
        to append a state and time to the `state` and
        `time` lists
        
        Parameters
        ----------
        time : float
            time after last time to commit from
        state : Vec
            state to commit at corresponding time
        '''
        pass
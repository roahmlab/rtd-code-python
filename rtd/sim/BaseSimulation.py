from abc import ABCMeta, abstractmethod
from rtd.sim.types import SimulationState



class BaseSimulation(metaclass=ABCMeta):
    def __init__(self):
        self.simulation_state: SimulationState = SimulationState.INVALID
        self.simulation_timestep: float = None
    
    @abstractmethod
    def add_object(self, object):
        '''
        Add some object to the simulation
        '''
        pass
    
    @abstractmethod
    def setup(self):
        '''
        Setup all the world
        '''
        pass
    
    @abstractmethod
    def initialize(self):
        '''
        Initialize everything to start
        '''
        pass
    
    @abstractmethod
    def pre_step(self):
        '''
        Execute before the overall step
        '''
        pass
    
    @abstractmethod
    def step(self):
        '''
        Execute all the updates needed for each step
        '''
        pass
    
    @abstractmethod
    def post_step(self):
        '''
        Execute after each step
        '''
        pass
    
    @abstractmethod
    def summary(self, **options):
        '''
        Generate the summary
        '''
        pass
    
    @abstractmethod
    def run(self, **options):
        '''
        Run the lifecycle.
        Max iterations or max length is embedded in this
        '''
        pass
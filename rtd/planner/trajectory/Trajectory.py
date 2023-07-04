from abc import ABCMeta, abstractmethod
from rtd.entity.states import EntityState
from rtd.planner.trajopt import TrajOptProps
from nptyping import NDArray, Shape, Float64

# type hinting
ColVec = NDArray[Shape['N,1'], Float64]



class Trajectory(metaclass=ABCMeta):
    '''
    Base class for a parameterized trajectory
    
    This encapsulates the conversion of parameters used in optimization to
    the actual trajectory generated from those parameters. This can also be
    used by an `Objective` object as part of the objective function call.
    It should be generated with some `TrajectoryFactory`
    '''
    def __init__(self):
        # Properties from the trajectory optimization, which also describes
        # the properties for the trajectory
        self.trajOptProps: TrajOptProps = None
        
        # The parameters used for this trajectory
        self.trajectoryParams: ColVec = None
        
        # The initial state for this trajectory
        self.startState: EntityState = None
        
        # Set to true if this trajectory supports getting commands for a
        # time vector instead of just a single moment in time
        self.vectorized = False
    
    
    @abstractmethod
    def validate(self, throwOnError: bool = False) -> bool:
        '''
        Validates if the trajectory is parameterized right
        
        A validation method to ensure that the trajectory this object
        describes is fully set. Has an additional argument to allow
        throwing an error if incorrect
        
        Arguments:
            throwOnError: bool: whether or not to throw an error if invalid
        
        Returns:
            bool: whether or not the trajectory is valid
        '''
        pass
    
    
    @abstractmethod
    def setParameters(self, trajectoryParams: ColVec, **options):
        '''
        Set the parameters for the trajectory
        
        This allows for the entire trajectory described to be changed,
        but it should focus on this trajectory params while the
        constructor should focus on the start state
        
        Arguments:
            trajectoryParams: the parameters of the trajectory to set
        '''
        pass
    
    
    @abstractmethod
    def getCommand(self, time: float | ColVec) -> EntityState:
        '''
        Computes the actual state to track for the given time
        
        Should throw RTD:InvalidTrajectory if the trajectory isn't set
        Should take ColVector as `time` if `vectorized` is True
        
        Arguments:
            time: Time to use to calculate the desired state for this trajectory
        
        Returns:
            EntityState: Desired state at the given time
        '''
        pass
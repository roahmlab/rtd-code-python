from abc import ABCMeta, abstractmethod
from rtd.entity.states import EntityState
from rtd.planner.trajopt import TrajOptProps
from rtd.planner.trajectory import Trajectory
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
ColVec = NDArray[Shape['N,1'], Float64]



class TrajectoryFactory(metaclass=ABCMeta):
    '''
    Base class for the Trajectory factory object
    
    This should be used to initialize desired instaces of
    `rtd.planner.trajectory.Trajectory`
    '''
    def __init__(self):
        # Properties from the trajectory optimization, which also describe
        # properties for a trajectory
        self.trajOptProps: TrajOptProps = None
    
    
    @abstractmethod
    def createTrajectory(self, robotState: EntityState, rsInstances: dict = None,
                         trajectoryParams: ColVec = None, **options) -> Trajectory:
        '''
        Factory method to create the trajectory
        
        This method constructs any relevant Trajectory objects and fully
        parameterizes them if desired. Additional options can be set in
        here, or handled in the class properties
        
        Arguments:
            robotState: EntityState: Initial state of the robot
            rsInstances: dict: Optional dict holding instances of reachablesets for the given state
            trajectoryParms: Optional parameters to fully parameterize the trajectories generated
        
        Returns:
            Trajectory: Desired Trajectory Object
        '''
        pass
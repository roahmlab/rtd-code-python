from rtd.planner.trajectory import Trajectory
from rtd.planner.trajopt import TrajOptProps
from rtd.entity.states import ArmRobotState
from armour.reachsets import JRSInstance
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
ColVec = NDArray[Shape['N,1'], Float64]



class PiecewiseArmTrajectory(Trajectory):
    '''
    PiecewiseArmTrajectory
    The original ArmTD trajectory with piecewise accelerations
    '''
    def __init__(self, trajOptProps: TrajOptProps,
                 startState: ArmRobotState, jrsInstance: JRSInstance):
        '''
        The PiecewiseArmTrajectory constructor, which simply sets parameters and
        attempts to call internalUpdate, a helper function made for this
        class to update all other internal parameters once fully
        parameterized
        '''
        # initialize base classes
        Trajectory().__init__(self)
        # set properties
        self.vectorized = True
        self.trajOptProps = trajOptProps
        self.startState = startState
        self.jrsInstance = jrsInstance
        # precomputed values
        self.q_ddot: float = None
        self.q_peak: float = None
        self.q_dot_peak: float = None
        self.q_ddot_to_stop: float = None
        self.q_end: float = None
    
    
    def setParameters(self, trajectoryParams: ColVec, **options):
        '''
        Set the parameters of the trajectory, with a focus on the
        parameters as the state should be set from the constructor
        '''
        self.trajectoryParams = trajectoryParams
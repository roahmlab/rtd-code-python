from rtd.planner.trajectory import Trajectory, InvalidTrajectory
from rtd.entity.states import ArmRobotState
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
RowVec = NDArray[Shape['N'], Float64]



class ZeroHoldArmTrajectory(Trajectory):
    def __init__(self, startState: ArmRobotState):
        '''
        The ZeroHoldArmTrajectory constructor, which simply sets parameters and
        attempts to call internalUpdate, a helper function made for this
        class to update all other internal parameters once fully
        parameterized
        '''
        # initialize base classes
        Trajectory.__init__(self)
        # set properties
        self.vectorized = True
        self.startState = startState
    
    
    def setParameters(self, trajectoryParams: RowVec, startState: ArmRobotState = None):
        '''
        Set the parameters of the trajectory, with a focus on the
        parameters as the state should be set from the constructor
        '''
        if startState == None:
            self.startState = startState
        self.trajectoryParams = trajectoryParams
        self.startState = startState
    
    
    def validate(self, throwOnError: bool = False) -> bool:
        '''
        Validate that the trajectory is fully characterized
        '''
        # Make sure we actually have a robot state to work with
        valid = (self.startState != None)
        
        if not valid and throwOnError:
            raise InvalidTrajectory("Must have some existing robot state to use this!")
        return valid

    
    def getCommand(self, time: RowVec) -> ArmRobotState:
        '''
        Computes the actual input commands for the given time.
        throws InvalidTrajectory if the trajectory isn't set
        '''
        # Do a parameter check and time check, and throw if anything is
        # invalid
        self.validate(True)
        if np.any(time < self.startState.time):
            raise InvalidTrajectory("Invalid time provided to ZeroHoldArmTrajectory")

        # Make the state
        n_q = self.startState.q.size    # q: (n_q,)
        state = np.tile(np.reshape(np.append(self.startState.q,0), (n_q+1,1)), time.size)   # state: (n_q+1, n_time)
        pos_idx = np.arange(n_q)
        acc_vel_idx = np.ones(n_q, dtype=int)*n_q
        
        # Generate the output
        command = ArmRobotState(pos_idx, acc_vel_idx, acc_vel_idx)
        command.time = time
        command.state = state
        return command
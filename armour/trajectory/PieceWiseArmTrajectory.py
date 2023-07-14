from rtd.planner.trajectory import Trajectory, InvalidTrajectory
from rtd.planner.trajopt import TrajOptProps
from rtd.entity.states import ArmRobotState
from armour.reachsets import JRSInstance
from rtd.functional.vectools import rescale
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
RowVec = NDArray[Shape['N'], Float64]



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
    
    
    def setParameters(self, trajectoryParams: RowVec, startState: ArmRobotState = None,
                      jrsInstance: JRSInstance = None):
        '''
        Set the parameters of the trajectory, with a focus on the
        parameters as the state should be set from the constructor
        '''
        self.trajectoryParams = trajectoryParams
        if self.trajectoryParams.size > self.jrsInstance.n_q:
            self.trajectoryParams = self.trajectoryParams[:self.jrsInstance.n_q]
        if startState == None:
            self.startState = startState
        if jrsInstance == None:
            self.jrsInstance = jrsInstance
        
        # perform internal update
        self.internalUpdate()
    
    
    def validate(self, throwOnError: bool = False) -> bool:
        '''
        Validate that the trajectory is fully characterized
        '''
        # non-empty
        valid = (self.trajectoryParams != None)
        valid &= (self.jrsInstance != None)
        valid &= (self.startState != None)
        
        # trajectory params makes sense
        valid &= (self.trajectoryParams.size == self.jrsInstance.n_q)
        
        # throw error if wanted
        if not valid and throwOnError:
            raise InvalidTrajectory("Called trajectory object does not have complete parameterization!")
        return valid

    
    def internalUpdate(self):
        '''
        Update internal parameters to reduce long term calculations
        '''
        # rename variables
        q_0 = self.startState.position
        q_dot_0 = self.startState.velocity
        
        # scale the parameters
        jout = self.jrsInstance.output_range
        jin = self.jrsInstance.input_range
        self.q_ddot = rescale(self.trajectoryParams, jout[0], jout[1], jin[0], jin[1])
        
        # compute the peak parameters
        self.q_peak = q_0 + q_dot_0*self.trajOptProps.planTime + 0.5*self.q_ddot*self.trajOptProps.planTime**2
        self.q_dot_peak = q_dot_0 + self.q_ddot*self.trajOptProps.planTime

        # compute the stopping parameters
        self.q_ddot_to_stop = (0-self.q_dot_peak) / (self.trajOptProps.horizonTime-self.trajOptProps.planTime)
        self.q_end = (self.q_peak + self.q_dot_peak*self.trajOptProps.planTime
                      + 0.5*self.q_ddot_to_stop*self.trajOptProps.planTime**2)
    
    
    def getCommand(self, time: RowVec) -> ArmRobotState:
        '''
        Computes the actual input commands for the given time.
        throws InvalidTrajectory if the trajectory isn't set
        '''
        # Do a parameter check and time check, and throw if anything is
        # invalid.
        self.validate(throwOnError=True)
        t_shifted = time - self.startState.time
        if t_shifted < 0:
            raise InvalidTrajectory("Invalid time provided to PiecewiseArmTrajectory")

        # Mask the first and second half of the trajectory
        t_plan_mask = t_shifted < self.trajOptProps.planTime
        t_stop_mask = (t_shifted < self.trajOptProps.horizonTime) ^ t_plan_mask
        t_plan_vals = t_shifted[t_plan_mask]
        t_stop_vals = t_shifted[t_stop_mask] - self.trajOptProps.planTime

        # Create the combined state variable
        t_size = time.size
        n_q = self.jrsInstance.n_q
        pos_idx = np.arange(n_q)
        vel_idx = pos_idx + n_q
        acc_idx = vel_idx + n_q
        state = np.zeros((n_q*3, t_size))
        
        # Rename variables
        q_0 = self.startState.position
        q_dot_0 = self.startState.velocity

        # Compute the first half of the trajectory
        if np.any(t_plan_mask):
            state[np.ix_(pos_idx,t_plan_mask)] = q_0 + q_dot_0*t_plan_vals + 0.5*self.q_ddot*t_plan_vals**2
            state[np.ix_(vel_idx,t_plan_mask)] = q_dot_0 + self.q_ddot*t_plan_vals
            state[np.ix_(acc_idx,t_plan_mask)] = self.q_ddot
        
        # Compute the second half of the trajectory
        if any(t_stop_mask):
            state[np.ix_(pos_idx,t_stop_mask)] = (self.q_peak + self.q_dot_peak*t_stop_vals
                                                  + 0.5*self.q_ddot_to_stop*t_stop_vals**2)
            state[np.ix_(vel_idx,t_stop_mask)] = self.q_dot_peak + self.q_ddot_to_stop*t_stop_vals
            state[np.ix_(acc_idx,t_stop_mask)] = self.q_ddot_to_stop

        # Update all states after the horizon time
        state[np.ix_(pos_idx, np.logical_not(t_plan_mask|t_stop_mask))] = self.q_end

        # Generate the output.
        command = ArmRobotState(pos_idx, vel_idx, acc_idx)
        command.time = time
        command.state = state
        
        return command
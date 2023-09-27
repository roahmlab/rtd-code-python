from rtd.planner.trajectory import Trajectory, InvalidTrajectory
from rtd.entity.states import ArmRobotState, EntityState
from rtd.planner.trajopt import TrajOptProps
from rtd.functional.vectools import rescale
from armour.reachsets import JRSInstance
from armour.legacy import bernstein_to_poly, match_deg5_bernstein_coefficients
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
RowVec = NDArray[Shape['N'], Float64]



class BernsteinArmTrajectory(Trajectory):
    def __init__(self, trajOptProps: TrajOptProps, startState: ArmRobotState, jrsInstance: JRSInstance):
        # initialize base classes
        Trajectory.__init__(self)
        # set properties
        self.vectorized = True
        # Initial parameters from the robot used to calculate the desired
        # trajectory
        self.alpha = None
        self.q_end = None
        # The JRS which contains the center and range to scale the
        # parameters
        self.jrsInstance = None
        # other properties
        self.trajOptProps = trajOptProps
        self.startState = startState
        self.jrsInstance = jrsInstance
    
    
    def setParameters(self, trajectoryParams: RowVec, startState: ArmRobotState = None,
                      jrsInstance: JRSInstance = None):
        '''
        A validated method to set the parameters for the trajectory
        '''
        self.trajectoryParams = trajectoryParams
        if self.trajectoryParams.size > self.jrsInstance.n_q:
            self.trajectoryParams = self.trajectoryParams[:self.jrsInstance.n_q]
        if startState is not None:
            self.startState = startState
        if jrsInstance is not None:
            self.jrsInstance = jrsInstance
        
        # perform internal update
        self.internalUpdate()
    
    
    def validate(self, throwOnError: bool = False) -> bool:
        '''
        Validate that the trajectory is fully characterized
        '''
        # non-empty
        valid = (self.trajectoryParams is not None)
        valid &= (self.jrsInstance is not None)
        valid &= (self.startState is not None)
        
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
        # internal update if valid
        if not self.validate():
            return
        
        # get the desired final position
        jout = self.jrsInstance.output_range
        jin = self.jrsInstance.input_range
        q_goal = rescale(self.trajectoryParams, jout[0], jout[1], jin[0], jin[1])
        q_goal = self.startState.q + q_goal
        
        n_q = self.jrsInstance.n_q
        self.alpha = np.zeros((n_q, 6))
        for j in range(n_q):
            beta = match_deg5_bernstein_coefficients([
                self.startState.position[j],
                self.startState.velocity[j],
                self.startState.acceleration[j],
                q_goal[j],
                0, 0],
                self.trajOptProps.horizonTime
            )
            self.alpha[j,:] = bernstein_to_poly(beta, 6)
        
        # precompute end position
        self.q_end = q_goal
    
    
    def getCommand(self, time: RowVec) -> EntityState:
        # Do a parameter check and time check, and throw if anything is
        # invalid.
        self.validate(throwOnError=True)
        t_shifted = np.atleast_1d(np.asarray(time - self.startState.time))
        if np.any(t_shifted < 0):
            raise InvalidTrajectory("Invalid time provided to PiecewiseArmTrajectory")

        t_size = t_shifted.size
        horizon_mask = t_shifted < self.trajOptProps.horizonTime
        t_masked_scaled = t_shifted[horizon_mask] / self.trajOptProps.horizonTime
        t_masked_size = t_masked_scaled.size
        n_q = self.jrsInstance.n_q
        
        # original implementation adapted
        q_des = np.zeros((n_q, t_masked_size))
        q_dot_des = np.zeros((n_q, t_masked_size))
        q_ddot_des = np.zeros((n_q, t_masked_size))
        
        for j in range(n_q):
            for coef_idx in range(6):
                q_des[j,:] += self.alpha[j,coef_idx]*np.power(t_masked_scaled, coef_idx)
                if coef_idx > 0:
                    q_dot_des[j,:] += coef_idx*self.alpha[j,coef_idx]*np.power(t_masked_scaled, coef_idx-1)
                if coef_idx > 1:
                    q_ddot_des[j,:] += coef_idx*(coef_idx-1)*self.alpha[j,coef_idx]*np.power(t_masked_scaled, coef_idx-2)
        
        # move to a combined state variable
        pos_idx = np.arange(n_q)
        vel_idx = pos_idx + n_q
        acc_idx = vel_idx + n_q
        state = np.zeros((n_q*3, t_size))
        state[np.ix_(pos_idx, horizon_mask)] = q_des
        state[np.ix_(vel_idx, horizon_mask)] = q_dot_des / self.trajOptProps.horizonTime
        state[np.ix_(acc_idx, horizon_mask)] = q_ddot_des / self.trajOptProps.horizonTime**2
        
        # update all state times after the horizon time
        state[np.ix_(pos_idx, np.logical_not(horizon_mask))] = np.reshape(self.q_end, (self.q_end.size,1))
        
        # Generate the output.
        command = ArmRobotState(pos_idx, vel_idx, acc_idx)
        command.time = time
        command.state = state
        
        return command
from rtd.entity.components import BaseStateComponent
from rtd.entity.states import ArmRobotState
from rtd.util.mixins import Options
from armour.agent import ArmourAgentInfo
from rtd.functional.interpolate import interp1_list
import numpy as np
from nptyping import NDArray, Shape, Float64

# define top level module logger
import logging
logger = logging.getLogger(__name__)

# type hinting
BoundsVec = NDArray[Shape['N,2'], Float64]



class ArmourAgentState(BaseStateComponent, Options):
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "components": {
                "initial_position": None,
                "initial_velocity": None,
            },
        }
    
    
    def __init__(self, arm_info: ArmourAgentInfo, **options):
        # initialize base classes
        BaseStateComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.entityinfo = arm_info
        # self.reset()
    
    
    @property
    def position(self):
        return self.state[self.position_indices,:]
    
    
    @property
    def velocity(self):
        return self.state[self.velocity_indices,:]
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        # Set component dependent properties
        self.n_states = 2 * self.entityinfo.n_q
        self.position_indices = np.arange(0, self.n_states, 2)
        self.velocity_indices = np.arange(1, self.n_states, 2)
        
        logger.info("Resetting time and states")
        self.state: NDArray = np.zeros((self.n_states, 1))
        self.time = np.zeros(1)
        self.step_start_idxs = np.zeros(1)
        
        # add position
        if options["initial_position"] is not None:
            logger.debug("Using provided joint positions")
            self.state[self.position_indices] = options["initial_position"]
        
        # add velocity
        if options["initial_velocity"] is not None:
            logger.debug("Using provided joint velocities")
            self.state[self.velocity_indices] = options["initial_velocity"]
        
        # take these initials and merge them in again
        options["initial_position"] = self.position
        options["initial_velocity"] = self.velocity
        self.mergeoptions(options)
    
    
    def random_init(self, pos_range: BoundsVec = None, vel_range: BoundsVec = None,
                    random_position: bool = True, random_velocity: bool = False,
                    save_to_options: bool = False):
        if pos_range is None:
            pos_range = self.entityinfo.joints[:self.entityinfo.n_q].position_limits
        if vel_range is None:
            vel_range = self.entityinfo.joints[:self.entityinfo.n_q].velocity_limits
        
        # set any joint limits that are +Inf to pi and -Inf to -pi
        pos_range_infs = np.isinf(pos_range)
        pos_range[0, pos_range_infs[0,:]] = -np.pi
        pos_range[1, pos_range_infs[1,:]] = np.pi
        
        # reset
        self.state: NDArray = np.zeros((self.n_states, 1))
        self.time = np.zeros(1)
        self.step_start_idxs = np.zeros(1)
        
        # make the random configuration
        if random_position:
            self.state[self.position_indices] = np.random.uniform(pos_range[0,:], pos_range[1,:])
        if random_velocity:
            self.state[self.velocity_indices] = np.random.uniform(vel_range[0,:], vel_range[1,:])
        
        if save_to_options:
            self.mergeoptions({"initial_position": self.position, "initial_velocity": self.velocity})
    
    
    def get_state(self, time: float = None) -> dict:
        if time is None:
            time = self.time[-1]
        state = ArmRobotState(self.position_indices, self.velocity_indices)
        
        # default to the last time and state
        state.time = time
        state.state = np.tile(self.state[:,-1], time.size)
        
        # if we can and need to interpolate the state, do it
        mask = time <= self.time[-1]
        if mask.size > 1 and np.any(mask):
            for n in self.n_states:
                state.state[n, mask] = np.interp(time[mask], time, self.state[n,:])
    
    
    def commit_state_data(self, T_state: float, Z_state: list[float]):
        '''
        method: commit_move_data(T_state,Z_state)
        
        After moving the agent, commit the new state and input
        trajectories, and associated time vectors, to the agent's
        state, time, input, and input_time properties
        '''
        # update the time and state
        self.step_start_idxs = np.append(self.time, self.time.size+1)
        self.time = np.concatenate((self.time, self.time[-1], T_state[1:]))
        self.state = np.concatenate((self.state, Z_state[:,1:]), 1)
    
    
    def joint_limit_check(self, t_check_step):
        # create time vector for checking
        start_idx = self.step_start_idxs[-1]
        t_check = np.arange(self.time[start_idx], self.time[-1], t_check_step)
        
        # get agent state trajectories interpolated to time
        pos_check = [np.interp(t_check, self.time[start_idx:], self.position[n,start_idx:]) for n in range(self.position.shape[0])]
        vel_check = [np.interp(t_check, self.time[start_idx:], self.velocity[n,start_idx:]) for n in range(self.velocity.shape[0])]
        
        logger.info("Running joint limits check!")
        
        # check position & velocity
        pos_exceeded = np.zeros(pos_check.shape, dtype=bool)
        vel_exceeded = np.zeros(vel_check.shape, dtype=bool)
        for i in range(self.entityinfo.n_q):
            # pos
            lb = pos_check[i,:] < self.entityinfo.joints[i].position_limits[0]
            ub = pos_check[i,:] > self.entityinfo.joints[i].position_limits[1]
            pos_exceeded[i,:] = lb | ub
            # vel
            lb = vel_check[i,:] < self.entityinfo.joints[i].velocity_limits[0]
            ub = vel_check[i,:] > self.entityinfo.joints[i].velocity_limits[1]
            vel_exceeded[i,:] = lb | ub
        
        # get out results
        out = np.any(pos_exceeded) | np.any(vel_exceeded)
        
        if out:
            # position limits exceeded in these positions
            idx_list = np.argwhere(pos_exceeded)
            for joint, t in idx_list:
                lb = self.entity_info.joints[joint].position_limits[0]
                ub = self.entity_info.joints[joint].position_limits[1]
                logger.error(f"t={t_check[t]:.2f}, {joint}-position limit exceeded: {pos_check[joint,t]:.5f}, [{lb:.5f},{ub:.5f}]")
            # velocity limits exceeded in these positions
            idx_list = np.argwhere(vel_exceeded)
            for joint, t in idx_list:
                lb = self.entity_info.joints[joint].velocity_limits[0]
                ub = self.entity_info.joints[joint].velocity_limits[1]
                logger.error(f"t={t_check[t]:.2f}, {joint}-velocity limit exceeded: {vel_check[joint,t]:.5f}, [{lb:.5f},{ub:.5f}]")
        else:
            logger.info("No joint limits exceeded")
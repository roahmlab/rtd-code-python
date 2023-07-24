from typing import Callable
from rtd.planner.reachsets import ReachSetInstance
from rtd.sim.world import WorldState
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
BoundsVec = NDArray[Shape['N,2'], Float64]



class JRSInstance(ReachSetInstance):
    '''
    JRSInstance
    This is just an individual instance of an original ARMTD JRS
    '''
    def __init__(self):
        # initialize base classes
        ReachSetInstance.__init__(self)
        # set properties
        self.input_range: BoundsVec = (-1.0, 1.0)
        self.output_range: BoundsVec = (-1.0, 1.0)
        self.num_parameters = 0
        
        # properties carried over from the original implementation
        self.q_des = None
        self.dq_des = None
        self.ddq_des = None
        self.q = None
        self.dq = None
        self.dq_a = None
        self.ddq_a = None
        self.R_des = None
        self.R_t_des = None
        self.R = None
        self.R_t = None
        self.jrs_info = None
        
        # new properties to flatten structure
        self.n_q = None
        self.n_t = None
        self.k_id = None
        self.n_k = None
        
    
    def initialize(self, traj_type: str):
        if self.traj_type == "piecewise":
            c_k = self.jrs_info.c_k_orig
            g_k = self.jrs_info.g_k_orig
        elif self.traj_type == "bernstein":
            c_k = self.jrs_info.c_k_bernstein
            g_k = self.jrs_info.g_k_bernstein
        self.input_range = np.ones((self.jrs_info.n_k, 1)) * self.input_range
        self.output_range = c_k + (-1, 1) * g_k
        
        self.n_q = self.jrs_info.n_q
        self.num_parameters = self.jrs_info.n_k
        self.n_k = self.jrs_info.n_k
        self.n_t = self.jrs_info.n_t
        self.k_id = self.jrs_info.k_id
    
    
    def genNLConstraint(self, worldState: WorldState) -> Callable:
        '''
        Handles the obstacle-frs pair or similar to generate the
        nlconstraint.
        Returns a function handle for the nlconstraint generated
        where the function's return type is [c, ceq, gc, gceq]
        '''
        return None
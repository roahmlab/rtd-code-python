from typing import Callable
from rtd.planner.reachsets import ReachSetInstance
from rtd.sim.world import WorldState
from armour.reachsets import JRSInstance
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
BoundsVec = NDArray[Shape['N,2'], Float64]



class JLSInstance(ReachSetInstance):
    '''
    IRSInstance
    This is just an individual instance of input reachable set from
    armour
    '''
    def __init__(self, q_ub, q_lb, dq_ub, dq_lb, jrsInstance: JRSInstance):
        # initialize base classes
        ReachSetInstance().__init__(self)
        
        # properties carried over from the original implementation
        self.q_ub = q_lb
        self.q_lb = q_lb
        self.dq_ub = dq_ub
        self.dq_lb = dq_lb
        self.n_q = jrsInstance.n_q
        self.n_t = jrsInstance.n_t
        self.num_parameters = jrsInstance.n_k
        self.input_range: BoundsVec = jrsInstance.input_range
    
    
    def genNLConstraint(self, worldState: WorldState) -> Callable:
        '''
        Generates an nlconstraint if needed, or will return a NOP
        function.
        Returns a function handle for the nlconstraint generated
        where the function's return type is [c, ceq, gc, gceq]
        '''
        pass
from typing import Callable
from rtd.planner.reachsets import ReachSetInstance
from rtd.sim.world import WorldState
from armour.reachsets import JRSInstance
from zonopy.conSet.polynomial_zonotope.poly_zono import polyZonotope
import numpy as np
from nptyping import NDArray, Shape, Float64

# define top level module logger
import logging
logger = logging.getLogger(__name__)

# type hinting
BoundsVec = NDArray[Shape['N,2'], Float64]



class IRSInstance(ReachSetInstance):
    '''
    IRSInstance
    This is just an individual instance of input reachable set from
    armour
    '''
    def __init__(self, u_ub: list[list[polyZonotope]], u_lb: list[list[polyZonotope]], jrsInstance: JRSInstance):
        # initialize base classes
        ReachSetInstance().__init__(self)
        
        # properties carried over from the original implementation
        self.u_ub: list[list[polyZonotope]] = u_ub
        self.u_lb: list[list[polyZonotope]] = u_lb
        self.n_q = jrsInstance.n_q
        self.n_t = jrsInstance.n_t
        self.num_parameters = jrsInstance.n_k
        self.input_range: BoundsVec = jrsInstance.input_range
    
    
    def genNLConstraint(self, worldState: WorldState) -> Callable:
        constraints: list [Callable] = list()
        grad_constraints: list [Callable] = list()
        
        # joint limit constraints
        for i in range(self.n_t):
            for j in range(self.n_q):
                # check if constraint necessary, then add
                u_ub_int = self.u_ub[i][j].to_interval()
                if u_ub_int.sup >= 0:
                    logger.debug(f"ADDED UPPER BOUND INPUT CONSTRAINT ON JOINT {j} AT TIME {i} \n")
                    constraints.append(lambda k : self.u_ub[i][j].slice_all_dep(k))
                    grad_u_ub = self.u_ub[i][j].grad_center_slice_all_dep(self.n_q)
                    grad_constraints.append(lambda k : [grad.slice_all_dep(k) for grad in grad_u_ub])
                
                u_lb_int = self.u_lb[i][j].to_interval()
                if u_lb_int.sup >= 0:
                    logger.debug(f"ADDED LOWER BOUND INPUT CONSTRAINT ON JOINT {j} AT TIME {i} \n")
                    constraints.append(lambda k : self.u_lb[i][j].slice_all_dep(k))
                    grad_u_lb = self.u_lb[i][j].grad_center_slice_all_dep(self.n_q)
                    grad_constraints.append(lambda k : [grad.slice_all_dep(k) for grad in grad_u_lb])
        
        return lambda k : self.eval_constraints(k, len(constraints), constraints, grad_constraints)     
    
    
    @staticmethod
    def eval_constraints(k, n_c: int, constraints: list[Callable], grad_constraints: list[Callable]):
        '''
        Note: remember that smooth constraints still need to be considered
        '''
        h = np.zeros(n_c)
        grad_h = np.zeros((k.size, n_c))
        
        for i in range(n_c):
            h[i] = constraints[i](k)
            grad_h[:,i] = grad_constraints[i](k)
        
        grad_heq = None
        heq = None
        return (h, heq, grad_h, grad_heq)
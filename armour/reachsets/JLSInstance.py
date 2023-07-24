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



class JLSInstance(ReachSetInstance):
    '''
    IRSInstance
    This is just an individual instance of input reachable set from
    armour
    '''
    def __init__(self, q_ub: list[list[polyZonotope]], q_lb: list[list[polyZonotope]], 
                 dq_ub: list[list[polyZonotope]], dq_lb: list[list[polyZonotope]], jrsInstance: JRSInstance):
        # initialize base classes
        ReachSetInstance().__init__(self)
        
        # properties carried over from the original implementation
        self.q_ub: list[list[polyZonotope]] = q_ub
        self.q_lb: list[list[polyZonotope]] = q_lb
        self.dq_ub: list[list[polyZonotope]] = dq_ub
        self.dq_lb: list[list[polyZonotope]] = dq_lb
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
        constraints: list [Callable] = list()
        grad_constraints: list [Callable] = list()
        
        # joint limit constraints
        for i in range(self.n_t):
            for j in range(self.n_q):
                # check if constraint necessary, then add
                q_ub_int = self.q_ub[i][j].to_interval()
                if q_ub_int.sup >= 0:
                    logger.debug(f"ADDED UPPER BOUND JOINT POSITION CONSTRAINT ON JOINT {j} AT TIME {i} \n")
                    constraints.append(lambda k : self.q_ub[i][j].slice_all_dep(k))
                    grad_q_ub = self.q_ub[i][j].grad_center_slice_all_dep(self.n_q)
                    grad_constraints.append(lambda k : [grad.slice_all_dep(k) for grad in grad_q_ub])
                
                q_lb_int = self.q_lb[i][j].to_interval()
                if q_lb_int.sup >= 0:
                    logger.debug(f"ADDED LOWER BOUND JOINT POSITION CONSTRAINT ON JOINT {j} AT TIME {i} \n")
                    constraints.append(lambda k : self.q_lb[i][j].slice_all_dep(k))
                    grad_q_lb = self.q_lb[i][j].grad_center_slice_all_dep(self.n_q)
                    grad_constraints.append(lambda k : [grad.slice_all_dep(k) for grad in grad_q_lb])
                
                dq_ub_int = self.dq_ub[i][j].to_interval()
                if dq_ub_int.sup >= 0:
                    logger.debug(f"ADDED UPPER BOUND JOINT VELOCITY CONSTRAINT ON JOINT {j} AT TIME {i} \n")
                    constraints.append(lambda k : self.dq_ub[i][j].slice_all_dep(k))
                    grad_dq_ub = self.dq_ub[i][j].grad_center_slice_all_dep(self.n_q)
                    grad_constraints.append(lambda k : [grad.slice_all_dep(k) for grad in grad_dq_ub])
                
                dq_lb_int = self.dq_lb[i][j].to_interval()
                if dq_lb_int.sup >= 0:
                    logger.debug(f"ADDED LOWER BOUND JOINT VELOCITY CONSTRAINT ON JOINT {j} AT TIME {i} \n")
                    constraints.append(lambda k : self.dq_lb[i][j].slice_all_dep(k))
                    grad_dq_lb = self.dq_lb[i][j].grad_center_slice_all_dep(self.n_q)
                    grad_constraints.append(lambda k : [grad.slice_all_dep(k) for grad in grad_dq_lb])  
        
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
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



class FOInstance(ReachSetInstance):
    '''
    JLSInstance
    This is just an individual instance of joint limit set set from
    armour
    '''
    def __init__(self, robotInfo, R_w, p_w, FO, jrsInstance: JRSInstance, smooth_obs, obs_frs_combs):
        # initialize base classes
        ReachSetInstance.__init__(self)
        
        # properties carried over from the original implementation
        self.robotInfo = robotInfo
        self.R_w = R_w
        self.p_w = p_w
        self.FO = FO
        self.jrsInstance = jrsInstance
        self.smooth_obs = smooth_obs
        self.num_parameters = jrsInstance.n_k
        self.input_range: BoundsVec = jrsInstance.input_range
        # initialize combinations (for obstacle avoidance constraints)
        self.obs_frs_combs = obs_frs_combs
    
    
    def genNLConstraint(self, worldState: WorldState) -> Callable:
        '''
        Handles the obstacle-frs pair or similar to generate the
        nlconstraint.
        Returns a function handle for the nlconstraint generated
        where the function's return type is [c, ceq, gc, gceq]
        '''
        if self.smooth_obs:
            smooth_obs_constraints = list()
            smooth_obs_constraints_A = list()
            smooth_obs_lambda_index = list()
        else:
            obs_constraints = list()
        
        # obstacle avoidance constraints
        for i in range(self.jrsInstance.n_t)
            for j in range(self.robotInfo.params.pz_nominal.num_bodies):
                for obs in worldState.obstacles:    # for each obstacle
                    
                    # first, check if constraints in necessary
                    O_buf = [obs.Z, self.FO[i][j].G, self.FO[i][j].Grest]
                    A_obs, b_obs = polytope_PH(O_buf, self.obs_frs_combs)   # get polytope form
                    if not np.all(A_obs*self.FO[i][j].c - b_obs <= 0):
                        continue
    
    
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
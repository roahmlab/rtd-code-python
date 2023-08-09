from typing import Callable
from rtd.planner.reachsets import ReachSetInstance
from rtd.sim.world import WorldState
from armour.reachsets import JRSInstance
from zonopy.conSet.polynomial_zonotope.poly_zono import polyZonotope
from zonopy.conSet.zonotope.zono import zonotope
import torch
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
    def __init__(self, robotInfo, FO, jrsInstance: JRSInstance, obs_frs_combs):
        # initialize base classes
        ReachSetInstance.__init__(self)
        
        # properties carried over from the original implementation
        self.robotInfo = robotInfo
        self.FO: list[list[polyZonotope]] = FO
        self.jrsInstance = jrsInstance
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
        obs_constraints = list()
        
        # obstacle avoidance constraints
        for t in range(self.jrsInstance.n_t):
            for j in range(self.robotInfo.params.pz_nominal.num_bodies):
                for obs in worldState.obstacles:    # for each obstacle
                    
                    # first, check if constraints in necessary
                    O_buf = torch.vstack((obs.Z, self.FO[t][j].G, self.FO[t][j].Grest))
                    A_obs, b_obs = zonotope(O_buf).polytope(self.obs_frs_combs)   # get polytope form
                    if not np.all(A_obs*self.FO[t][j].c - b_obs <= 0):
                        continue
                        
                    # reduce FO so that polytope has fewer directions to consider
                    self.FO[t][j] = self.FO[t][j].reduce_indep(3)
                    
                    # now create constraints
                    FO_buf = self.FO[t][j].Grest    # will buffer by non-sliceable gens
                    O_buf = torch.vstack((obs.Z, FO_buf))         # describes buffered obstacle zonotope
                    A_obs, b_obs = zonotope(O_buf).polytope(self.obs_frs_combs)   # get polytope form
                    
                    # constraint pz
                    FO_tmp = polyZonotope(Z=torch.vstack((self.FO[t][j].c, self.FO[t][j].G)), n_dep_gens=self.FO[t][j].n_dep_gens, 
                                          expMat=self.FO[t][j].expMat, id=self.FO[t][j].id)
                    obs_constraint_pz: polyZonotope = A_obs*FO_tmp - b_obs
                    
                    # turn into function
                    obs_constraint_pz_slice = lambda k: obs_constraint_pz.slice_all_dep(k)
                    
                    # add gradients
                    grad_obs_constraint_pz_slice = lambda k: obs_constraint_pz.grad_center_slice_all_dep(k)
                    
                    # save
                    obs_constraints.append(lambda k: self.indiv_obs_constraint(obs_constraint_pz_slice, grad_obs_constraint_pz_slice, k))
        
        # create the constraint callback
        return lambda k: self.eval_constraints(k, len(obs_constraints), obs_constraints)
    
    
    def indiv_obs_constraint(self, c: Callable, grad_c: Callable, k) -> tuple[float, list]:
        '''
        Made a separate function to handle the obstacle constraints,
        because the gradient requires knowing the index causing
        the max of the constraints
        '''
        h_obs = -torch.max(c(k))
        grad_eval = grad_c(k)
        grad_h_obs = [-grad[-h_obs,:] for grad in grad_eval]
        return (h_obs, grad_h_obs)
        
    
    @staticmethod
    def eval_constraints(k, n_c: int, obs_constraints: list[Callable]):
        h = np.zeros(n_c)
        grad_h = np.zeros((k.size, n_c))
        
        for i in range(n_c):
            h[i], grad_h[:,i] = obs_constraints[i](k)
        
        grad_heq = None
        heq = None
        return (h, heq, grad_h, grad_heq)
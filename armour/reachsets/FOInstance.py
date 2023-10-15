from typing import Callable
from rtd.planner.reachsets import ReachSetInstance
from rtd.sim.world import WorldState
from armour.reachsets import JRSInstance
from zonopy import batchZonotope, batchPolyZonotope
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
    def __init__(self, FO, jrsInstance: JRSInstance, obs_frs_combs):
        # initialize base classes
        ReachSetInstance.__init__(self)
        
        # properties carried over from the original implementation
        self.FO: list[batchPolyZonotope] = FO
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
        for j in range(self.jrsInstance.n_q):
            for obs in worldState.obstacles:    # for each obstacle
                
                # first, check if constraints in necessary
                O_buf = torch.cat((obs.Z.expand(100, -1, -1), self.FO[j].G, self.FO[j].Grest), dim=1)
                A_obs, b_obs = batchZonotope(O_buf).polytope(self.obs_frs_combs)   # get polytope form
                h_overapprox = (A_obs@self.FO[j].c.unsqueeze(-1)).squeeze(-1) - b_obs
                if not (torch.max(h_overapprox.nan_to_num(-torch.inf),-1)[0] < 1e-6).any():     # no collision
                    continue
                    
                # reduce FO so that polytope has fewer directions to consider
                self.FO[j] = self.FO[j].reduce_indep(3)
                
                # now create constraints
                FO_buf = self.FO[j].Grest       # will buffer by non-sliceable gens
                O_buf = torch.cat((obs.Z.expand(100, -1, -1), FO_buf), dim=1)       # describes buffered obstacle zonotope
                A_obs, b_obs = batchZonotope(O_buf).polytope(self.obs_frs_combs)    # get polytope form
                
                # constraint pz
                FO_tmp = batchPolyZonotope(Z=self.FO[j].Z[...,:self.FO[j].n_dep_gens+1,:], n_dep_gens=self.FO[j].n_dep_gens, 
                                           expMat=self.FO[j].expMat, id=self.FO[j].id)
                obs_constraint_pz = A_obs@FO_tmp - b_obs
                
                # turn into function
                obs_constraint_pz_slice = lambda k: obs_constraint_pz.cpu().center_slice_all_dep(k)
                
                # add gradients
                grad_obs_constraint_pz_slice = lambda k: obs_constraint_pz.cpu().grad_center_slice_all_dep(k)
                
                # save
                obs_constraints.append(lambda k: self.batch_obs_constraint(obs_constraint_pz_slice, grad_obs_constraint_pz_slice, torch.from_numpy(k).float()))
        
        # create the constraint callback
        return lambda k: self.eval_constraints(k, len(obs_constraints), obs_constraints, batch_size=100)
    

    def batch_obs_constraint(self, c: Callable, grad_c: Callable, k) -> tuple[float, list]:
        '''
        Made a separate function to handle the obstacle constraints,
        because the gradient requires knowing the index causing
        the max of the constraints
        '''
        h_obs, max_idx = torch.max(c(k).nan_to_num(-torch.inf), -1)
        grad_eval = grad_c(k)
        grad_h_obs = grad_eval[torch.arange(grad_eval.shape[0]),max_idx,:]
        # grad_h_obs = [-grad[-h_obs,:] for grad in grad_eval]
        return (-h_obs.numpy(), grad_h_obs.numpy())
        
    
    @staticmethod
    def eval_constraints(k, n_c: int, obs_constraints: list[Callable], batch_size: int = 1):
        h = np.zeros(n_c*batch_size)
        grad_h = np.zeros((n_c*batch_size, k.size))
        
        for i in range(n_c):
            h[i*batch_size:(i+1)*batch_size], grad_h[i*batch_size:(i+1)*batch_size,:] = obs_constraints[i](k)
        
        grad_heq = None
        heq = None
        return (h, heq, grad_h, grad_heq)
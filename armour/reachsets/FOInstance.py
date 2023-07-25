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
    def __init__(self, robotInfo, R_w, p_w, FO, jrsInstance: JRSInstance, smooth_obs, obs_frs_combs):
        # initialize base classes
        ReachSetInstance.__init__(self)
        
        # properties carried over from the original implementation
        self.robotInfo = robotInfo
        self.R_w = R_w
        self.p_w = p_w
        self.FO: list[list[polyZonotope]] = FO
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
            smooth_obs_lambda_index: list[list[int]] = list()
        else:
            obs_constraints = list()
        
        # obstacle avoidance constraints
        for i in range(self.jrsInstance.n_t):
            for j in range(self.robotInfo.params.pz_nominal.num_bodies):
                for obs in worldState.obstacles:    # for each obstacle
                    
                    # first, check if constraints in necessary
                    O_buf = [obs.Z, self.FO[i][j].G, self.FO[i][j].Grest]
                    A_obs, b_obs = zonotope(O_buf).polytope(self.obs_frs_combs)   # get polytope form
                    if not np.all(A_obs*self.FO[i][j].c - b_obs <= 0):
                        continue
                        
                    # reduce FO so that polytope has fewer directions to consider
                    self.FO[i][j] = self.FO[i][j].reduce(3)
                    
                    # now create constraints
                    FO_buf = self.FO[i][j].Grest    # will buffer by non-sliceable gens
                    O_buf = [obs.Z, FO_buf]         # describes buffered obstacle zonotope
                    A_obs, b_obs = zonotope(O_buf).polytope(self.obs_frs_combs)   # get polytope form
                    
                    # constraint pz
                    FO_tmp = polyZonotope(Z=[self.FO[i][j].c, self.FO[i][j].G], n_dep_gens=self.FO[i][j].n_dep_gens, 
                                          expMat=self.FO[i][j].expMat, id=self.FO[i][j].id)
                    obs_constraint_pz: polyZonotope = A_obs*FO_tmp - b_obs
                    
                    # turn into function
                    obs_constraint_pz_slice = lambda k: obs_constraint_pz.slice_all_dep(k)
                    
                    # add gradients
                    grad_obs_constraint_pz = obs_constraint_pz.grad_center_slice_all_dep(self.jrsInstance.n_q)
                    grad_obs_constraint_pz_slice = lambda k : [grad.slice_all_dep(k) for grad in grad_obs_constraint_pz]
                    
                    # save
                    if not self.smooth_obs:
                        obs_constraints.append(lambda k: self.indiv_obs_constraint(obs_constraint_pz_slice, grad_obs_constraint_pz_slice, k))
                    else:
                        smooth_obs_constraints_A.append(A_obs)
                        smooth_obs_constraints.append(lambda k, l: self.indiv_smooth_obs_constraint(obs_constraint_pz_slice, grad_obs_constraint_pz_slice, k, l))
                        if len(smooth_obs_lambda_index) == 0:
                            smooth_obs_lambda_index.append(np.arange(obs_constraint_pz.c.size))
                        else:
                            smooth_obs_lambda_index.append(smooth_obs_lambda_index[-1][-1] + np.arange(obs_constraint_pz.c.size))
        
        # update n_k and parameter_range if smooth
        if self.smooth_obs and len(smooth_obs_lambda_index) != 0:
            self.num_parameters = self.jrsInstance.num_parameters
            lambda_range = (0, smooth_obs_lambda_index[-1][-1])
            self.input_range = np.stack((self.jrsInstance.input_range, lambda_range))
        
        # create the constraint callback
        if self.smooth_obs:
            return lambda k: self.eval_smooth_constraints(k[:self.jrsInstance.n_k], k[self.jrsInstance.n_k+1:],
                                                          smooth_obs_constraints_A, smooth_obs_constraints,
                                                          smooth_obs_lambda_index)
        else:
            return lambda k: self.eval_constraints(k, len(obs_constraints), obs_constraints)
    
    
    def indiv_obs_constraint(self, c: Callable, grad_c: Callable, k) -> tuple[float, list]:
        '''
        Made a separate function to handle the obstacle constraints,
        because the gradient requires knowing the index causing
        the max of the constraints
        '''
        h_obs = -max(c(k))
        grad_eval = grad_c(k)
        grad_h_obs = [-grad[-h_obs,:] for grad in grad_eval]
        return (h_obs, grad_h_obs)
    
    
    def indiv_smooth_obs_constraint(self, c: Callable, grad_c: Callable, k, l) -> tuple[float, NDArray]:
        '''
        for evaluating smooth obs constraints, where lambda is introduced
        as extra decision variables to avoid taking a max
        '''
        # evaluate constraint: (A*FO - b)'*lambda
        h_obs = -c(k)*l
        
        # evaluate gradient w.r.t. k... 
        # grad_c(k) gives n_k x 1 cell, each containing
        # an N x 1 vector, where N is the number of rows of A.
        # take the dot product of each cell with lambda
        grad_eval = grad_c(k)
        grad_h_obs = [-grad*l for grad in grad_eval]
        
        # evaluate this gradient w.r.t. lambda
        # this is just (A*FO-b)
        grad_h_obs = np.stack((grad_h_obs, -c(k)))
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
    
    
    @staticmethod
    def eval_smooth_constraints(k, l, smooth_obs_constraints_A: list,
                                smooth_obs_constraints: list[Callable],
                                smooth_obs_lambda_index: list[NDArray]):
        n_obs_c = len(smooth_obs_constraints)
        n_k = k.size
        n_lambda = l.size

        h = np.zeros(2*n_obs_c)
        grad_h = np.zeros((n_k + n_lambda, 2*n_obs_c))
        
        for i in range(n_obs_c):
            lambda_idx = smooth_obs_lambda_index[i]
            lambda_i = l[lambda_idx]
            h[i], grad_h_i = smooth_obs_constraints[i](k, lambda_i)
            
            # obs avoidance constraints
            grad_h[:n_k, i] = grad_h_i[:n_k, 0]
            grad_h[n_k+lambda_idx, i] = grad_h_i[n_k+1:, 0]
            
            # from Borrelli paper
            h[n_obs_c+i] = torch.norm(smooth_obs_constraints_A[i]*lambda_i) - 1
            A_bar = smooth_obs_constraints_A[i]*torch.t(smooth_obs_constraints_A[i])
            grad_h[n_k+lambda_idx, n_obs_c+i] = 0.5*(np.transpose(lambda_i)*A_bar*lambda_i)**(-0.5)*2*A_bar*lambda_i
        
        grad_heq = None
        heq = None
        return (h, heq, grad_h, grad_heq)
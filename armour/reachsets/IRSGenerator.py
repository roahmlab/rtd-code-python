from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetGenerator
from armour.reachsets import IRSInstance, JRSGenerator
from zonopy.conSet.polynomial_zonotope.poly_zono import polyZonotope
from zonopy.dynamics.RNEA import poly_zono_rnea
import torch
import numpy as np

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class IRSGenerator(ReachSetGenerator):
    '''
    InputReachableSet
    This generates the upper and lower bound reachable sets on the input,
    and creates an IRSInstance object
    '''
    def __init__(self, robot, jrsGenerator: JRSGenerator, use_robost_input: bool = True):
        # initialize base classes
        ReachSetGenerator().__init__(self)
        # set properties
        self.cache_max_size = 1
        self.robot = robot
        self.jrsGenerator: JRSGenerator = jrsGenerator
        self.use_robost_input = use_robost_input
    
    
    def generateReachableSet(self, robotState: EntityState) -> dict[int, IRSInstance]:
        '''
        Obtains the relevant reachable set for the robotstate provided
        and outputs the singular instance of a reachable set
        '''
        # Computes the forward kinematics and occupancy
        # First get the JRS (allow the use of a cached value if it
        # exists
        jrsInstance = self.jrsGenerator.getReachableSet(robotState, ignore_cache=False)[1]
        
        logger.info("Generating input reachable set!")
        
        # set up zeros and overapproximation of r
        for j in range(jrsInstance.n_q):
            pass
        
        tau_nom: list[list] = list()
        for i in range(jrsInstance.n_t):
            f, n, u = poly_zono_rnea(jrsInstance.R[i], jrsInstance.R_t[i], jrsInstance.dq[i],
                                     jrsInstance.dq_a[i], jrsInstance.ddq_a[i], self.robot.info.params, True)
            tau_nom.append([u, f, n])
        
        v_norm = np.zeros(jrsInstance.n_t)
        
        # compute total input tortatotope
        u_ub: list[list[polyZonotope]] = list()
        u_lb: list[list[polyZonotope]] = list()
        
        # joint limit constraint setup
        for i in range(jrsInstance.n_t):
            u_ub.append(list())
            u_lb.append(list())
            
            for j in range(jrsInstance.n_q):
                u_ub_tmp = tau_nom[i][j] + v_norm[i]
                u_lb_tmp = tau_nom[i][j] - v_norm[i]
                u_ub_tmp = u_ub_tmp.reduce_indep(jrsInstance.k_id[-1])
                u_lb_tmp = u_lb_tmp.reduce_indep(jrsInstance.k_id[-1])
                u_ub_buf = torch.sum(torch.abs(u_ub_tmp.Grest))
                u_lb_buf = -torch.sum(torch.abs(u_lb_tmp.Grest))
                # assign bounds at [i][j]
                u_ub[i].append(polyZonotope(Z=[u_ub_tmp.c + u_ub_buf, u_ub_tmp.G], n_dep_gens=u_ub_tmp.n_dep_gens,
                                            expmat=u_ub_tmp.expMat, id=u_ub_tmp.id) - self.robot.joints[j].torque_limit[1])
                u_lb[i].append(polyZonotope(Z=[u_lb_tmp.c + u_lb_buf, u_lb_tmp.G], n_dep_gens=u_lb_tmp.n_dep_gens,
                                            expmat=u_lb_tmp.expMat, id=u_lb_tmp.id) - self.robot.joints[j].torque_limit[0])
                
        # Save the generated reachable sets into the JLSInstance
        return {1: IRSInstance(u_ub, u_lb, jrsInstance)}
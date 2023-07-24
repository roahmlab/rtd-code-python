from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetGenerator
from armour.reachsets import JLSInstance, JRSGenerator
from zonopy.conSet.polynomial_zonotope.poly_zono import polyZonotope
import torch
import numpy as np

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class JLSGenerator(ReachSetGenerator):
    '''
    InputReachableSet
    This generates the upper and lower bound reachable sets on the input,
    and creates an IRSInstance object
    '''
    def __init__(self, robot, jrsGenerator: JRSGenerator, **options):
        # initialize base classes
        ReachSetGenerator().__init__(self)
        # set properties
        self.cache_max_size = 1
        self.robot = robot
        self.jrsGenerator: JRSGenerator = jrsGenerator
    
    
    def generateReachableSet(self, robotState: EntityState) -> dict[int, JLSInstance]:
        '''
        Obtains the relevant reachable set for the robotstate provided
        and outputs the singular instance of a reachable set
        '''
        # Computes the forward kinematics and occupancy
        # First get the JRS (allow the use of a cached value if it
        # exists
        jrsInstance = self.jrsGenerator.getReachableSet(robotState, ignore_cache=False)[1]
        
        joint_state_limits = np.copy(self.robot.info.joints.position_limits)
        joint_speed_limits = np.copy(self.robot.info.joints.velocity_limits)
        joint_limit_infs = np.isinf(joint_state_limits)
        speed_limit_infs = np.isinf(joint_speed_limits);
        joint_state_limits[0,joint_limit_infs[0,:]] = -200*np.pi
        joint_state_limits[1,joint_limit_infs[1,:]] = +200*np.pi            
        joint_speed_limits[0,speed_limit_infs[0,:]] = -200*np.pi
        joint_speed_limits[1,speed_limit_infs[1,:]] = +200*np.pi
        
        logger.info("Generating joint limit set!")
        
        q_ub: list[list[polyZonotope]] = list()
        q_lb: list[list[polyZonotope]] = list()
        dq_ub: list[list[polyZonotope]] = list()
        dq_lb: list[list[polyZonotope]] = list()
        
        # joint limit constraint setup
        for i in range(jrsInstance.n_t):
            q_ub.append(list())
            q_lb.append(list())
            dq_ub.append(list())
            dq_lb.append(list())
            
            for j in range(jrsInstance.n_q):
                q_lim_tmp = jrsInstance.q[i][j]
                dq_lim_tmp = jrsInstance.dq[i][j]
                q_lim_tmp = q_lim_tmp.reduce_indep(jrsInstance.k_id[-1])
                dq_lim_tmp = dq_lim_tmp.reduce_indep(jrsInstance.k_id[-1])
                q_buf = torch.sum(torch.abs(q_lim_tmp.Grest))
                dq_buf = torch.sum(torch.abs(dq_lim_tmp.Grest))
                # assign bounds at [i][j]
                q_ub[i].append(polyZonotope(Z=[q_lim_tmp.c + q_buf, q_lim_tmp.G, list()], expmat=q_lim_tmp.expMat, id=q_lim_tmp.id) - joint_state_limits[1,j])
                q_lb[i].append(-1*polyZonotope(Z=[q_lim_tmp.c + q_buf, q_lim_tmp.G, list()], expmat=q_lim_tmp.expMat, id=q_lim_tmp.id) + joint_state_limits[0,j])
                dq_ub[i].append(polyZonotope(Z=[dq_lim_tmp.c + dq_buf, dq_lim_tmp.G, list()], expmat=dq_lim_tmp.expMat, id=dq_lim_tmp.id) - joint_speed_limits[1,j])
                dq_lb[i].append(-1*polyZonotope(Z=[dq_lim_tmp.c + dq_buf, dq_lim_tmp.G, list()], expmat=dq_lim_tmp.expMat, id=dq_lim_tmp.id) + joint_speed_limits[0,j])
                
        # Save the generated reachable sets into the JLSInstance
        return JLSInstance(q_ub, q_lb, dq_ub, dq_lb, jrsInstance)
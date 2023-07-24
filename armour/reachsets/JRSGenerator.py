from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetGenerator
from armour.reachsets import JRSInstance
from zonopy.joint_reachable_set.gen_jrs import JrsGenerator as ZonoJRSGenerator
import zonopy.trajectories as zpt
import numpy as np

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class JRSGenerator(ReachSetGenerator):
    '''
    JointReachableSetsOnline
    This does the online computation of joint reachable sets. It then
    generates a JRSInstance object
    '''
    def __init__(self, robot, taylor_degree: int = 1, add_ultimate_bound: bool = True,
                 traj_type: str = "piecewise"):
        # initialize base classes
        ReachSetGenerator().__init__(self)
        # set properties
        self.cache_max_size = 1
        self.controller = robot.controller
        self.taylor_degree = taylor_degree
        self.add_ultimate_bound = add_ultimate_bound
        self.traj_type = traj_type
        # initialize zonopy's JRSGenerator
        traj_class = zpt.PiecewiseArmTrajectory if traj_type=="piecewise" else zpt.BernsteinArmTrajectory
        self._jrnsgen = ZonoJRSGenerator(robot, traj_class)
    
    
    def generateReachableSet(self, robotState: EntityState) -> dict[int, JRSInstance]:
        '''
        Obtains the relevant reachable set for the robotstate provided
        and outputs the singular instance of a reachable set.
        Wraps create_jrs_online
        '''
        rs = JRSInstance()
        
        logger.info("Generating joint reachable set!")
        logger.info("The following message is from create_jrs_online")
        
        # generate it online
        # note: controller and ultimate_bounds not used unlike the original MATLAB implementation
        zonojrs = self._jrnsgen.gen_JRS(robotState.q, robotState.q_dot, robotState.q_ddot, self.taylor_degree)
        rs.q_des = zonojrs['q_ref']
        rs.dq_des = zonojrs['qd_ref']
        rs.ddq_des = zonojrs['qdd_ref']
        rs.q = zonojrs['q']
        rs.dq = zonojrs['qd']
        rs.dq_a = zonojrs['qd_aux']
        rs.ddq_a = zonojrs['qdd_aux']
        rs.R_des = zonojrs['R_ref']
        rs.R_t_des = zonojrs['']    # ???
        rs.R = zonojrs['R']
        rs.R_t = zonojrs['']        # ???
        
        n_q = rs.q.size
        n_k = n_q

        rs.jrs_info = {
            'id': 1,
            'id_names': None,
            'k_id': np.arange(n_q).reshape(n_q,1),
            'n_t': 1/0.01,
            'n_q': n_q,
            'n_k': n_k,
            'c_k_orig': np.zeros(n_k),
            'g_k_orig': np.min(np.max(np.pi/24, np.abs(rs.dq/3)), np.pi/3),
            'c_k_bernstein': np.zeros(n_q),
            'g_k_bernstein': np.pi/36 * np.ones(n_q),
        }
         
        # initialize this particular instance and run
        rs.initialize(self.traj_type)
        return {1: rs}
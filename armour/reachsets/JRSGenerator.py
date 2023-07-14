from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetGenerator
from armour.reachsets import JRSInstance
from armour.legacy import create_jrs_online

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
        self.cache_max_size = 1
        self.joint_axes = [robot.info.joints.axes]
        self.controller = robot.controller
        self.taylor_degree = taylor_degree
        self.add_ultimate_bound = add_ultimate_bound
        self.traj_type = traj_type
    
    
    def generateReachableSet(self, robotState: EntityState, **options) -> dict[int, JRSInstance]:
        '''
        Obtains the relevant reachable set for the robotstate provided
        and outputs the singular instance of a reachable set.
        Wraps create_jrs_online
        Returns JRSInstance
        '''
        rs = JRSInstance()
        traj_type_adapt = self.traj_type if self.traj_type!="piecewise" else "orig"
        
        logger.info("Generating joint reachable set!")
        logger.info("The following message is from create_jrs_online")
        # generate it online as it appears in the original implementation
        (rs.q_des, rs.dq_des, rs.ddq_des, rs.q, rs.dq, rs.dq_a, rs.ddq_a,
         rs.R_des, rs.R_t_des, rs.R, rs.R_t, rs.jrs_info) = create_jrs_online(
            robotState.q,
            robotState.q_dot,
            robotState.q_ddot,
            self.joint_axes,
            self.taylor_degree,
            traj_type_adapt,
            self.add_ultimate_bound,
            self.controller
        )
         
        # initialize this particular instance and run
        rs.initialize(self.traj_type)
        return {1: rs}
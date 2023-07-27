from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetGenerator
from armour.reachsets import FOInstance, JRSGenerator
from zonopy.conSet.polynomial_zonotope.poly_zono import polyZonotope
from itertools import combinations
import torch
import numpy as np

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class FOGenerator(ReachSetGenerator):
    '''
    ForwardOccupancy
    This acts as a generator for a single instance of a
    ForwardReachableSet, and return FOInstance
    '''
    def __init__(self, robot, jrsGenerator: JRSGenerator, smooth_obs: bool = False, obs_frs_combs: dict = None):
        # initialize base classes
        ReachSetGenerator.__init__(self)
        # set properties
        if obs_frs_combs is None:
            obs_frs_combs = {'maxcombs': 200, 'combs': None}
        self.cache_max_size = 0 # we don't want to cache any FO
        self.robot = robot
        self.jrsGenerator: JRSGenerator = jrsGenerator
        self.smooth_obs: bool = smooth_obs
        self.obs_frs_combs: dict = obs_frs_combs
        if self.obs_frs_combs['combs'] is None:
            self.obs_frs_combs['combs'] = self.generate_combinations_upto(self.obs_frs_combs['maxcombs'])
    
    
    def generateReachableSet(self, robotState: EntityState) -> dict[int, FOInstance]:
        '''
        Obtains the relevant reachable set for the robotstate provided
        and outputs the singular instance of a reachable set.
        Returns FOInstance
        '''
        jrsInstance = self.jrsGenerator.getReachableSet(robotState, ignore_cache=True)
        logger.info("Generating forward occupancy!")
        FO: list[list[polyZonotope]] = list()
        R_w = list[list] = list()
        p_w = list[list] = list()
        for i in range(jrsInstance.n_t):
            R_w_i, p_w_i = pzfk(jrsInstance.R[i], self.robot.info.params.pz_nominal)
            R_w.append(R_w_i)
            p_w.append(p_w_i)
            FO.append(list())
            for j in range(self.robot.info.params.pz_nominal.num_bodies):
                FO[i].append(R_w_i[j]*self.robot.info.links[j].poly_zonotope + p_w_i[j])
                FO[i][j] = FO[i][j].reduce(self.robot.info.params.pz_interval.zono_order)
                FO[i][j] = FO[i][j].reduce_indep(jrsInstance.k_id[-1])
        
        return FOInstance(self.robot.info, R_w, p_w, FO, jrsInstance, self.smooth_obs, self.obs_frs_combs)
                    
    
    @staticmethod
    def generate_combinations_upto(n: int) -> list[list[int]]:
        '''
        generate a bunch of combinations, store in a cell
        '''
        combs = [list(combinations(np.arange(i+1), 2)) for i in range(0, n)]
        combs[0].append(0)
        return combs
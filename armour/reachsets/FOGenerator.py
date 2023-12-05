from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetGenerator
from armour.reachsets import FOInstance, JRSGenerator
from zonopy import polyZonotope
from itertools import combinations
# from zonopy.kinematics import FO as FOcc
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
        forwardocc = list(forward_occupancy(jrsInstance[1].R, self.robot)[0].values())[1:jrsInstance[1].n_q+1]
        return {1: FOInstance(forwardocc, jrsInstance[1], self.obs_frs_combs)}
                    
    
    @staticmethod
    def generate_combinations_upto(n: int) -> list[list[int]]:
        '''
        generate a bunch of combinations, store in a cell
        '''
        combs = [list(combinations(np.arange(i+1), 2)) for i in range(0, n)]
        combs[0].append(0)
        return combs

# Pulled from zonopy-ext
from zonopy import polyZonotope, matPolyZonotope, batchPolyZonotope, batchMatPolyZonotope
from collections import OrderedDict
from zonopyrobots.kinematics import forward_kinematics
from zonopyrobots import ZonoArmRobot

from typing import Union, Dict, List, Tuple
from typing import OrderedDict as OrderedDictType

# Use forward kinematics to get the forward occupancy
# Note: zono_order=2 is 5 times faster than zono_order=20 on cpu
def forward_occupancy(rotatotopes: Union[Dict[str, Union[matPolyZonotope, batchMatPolyZonotope]],
                                         List[Union[matPolyZonotope, batchMatPolyZonotope]]],
                      robot: ZonoArmRobot,
                      zono_order: int = 20,
                      links: List[str] = None,
                      link_zono_override: Dict[str, polyZonotope] = None,
                      ) -> Tuple[OrderedDictType[str, Union[polyZonotope, batchPolyZonotope]],
                                 OrderedDictType[str, Union[Tuple[polyZonotope, matPolyZonotope],
                                                            Tuple[batchPolyZonotope, batchMatPolyZonotope]]]]:
    
    link_fk_dict = forward_kinematics(rotatotopes, robot, zono_order, links=links)
    urdf = robot.urdf
    link_zonos = {name: robot.link_data[urdf._link_map[name]].bounding_pz for name in link_fk_dict.keys()}
    if link_zono_override is not None:
        link_zonos.update(link_zono_override)
    
    fo = OrderedDict()
    for name, (pos, rot) in link_fk_dict.items():
        link_zono = link_zonos[name]
        fo_link = pos + rot@link_zono
        fo[name] = fo_link.reduce_indep(zono_order)
    
    return fo, link_fk_dict
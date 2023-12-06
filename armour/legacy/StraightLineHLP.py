from armour.agent import ArmourAgentInfo
import numpy as np
from rtd.util.mixins.Typings import Vecnp



class StraightLineHLP():
    def __init__(self):
        self.default_lookahead_distance: float = 1
        self.goal: Vecnp = None
        self.joint_state_indices: Vecnp = None
    
    
    def setup(self, agent_info: ArmourAgentInfo, world_info: dict):
        self.goal = world_info["goal"]
        self.arm_joint_state_indices = agent_info.joint_state_indices
        
    
    def get_waypoint(self, state: Vecnp, lookahead_distance: float = None) -> Vecnp:
        if lookahead_distance is None:
            lookahead_distance = self.default_lookahead_distance
        q_cur = state[self.arm_joint_state_indices]
        q_goal = self.goal
        dir_des = q_goal - q_cur
        dir_norm = np.linalg.norm(dir_des)
        
        # if we're close enough, just set the destination as the goal
        if dir_norm > lookahead_distance:
            dir_des = dir_des / dir_norm
            return q_cur + lookahead_distance*dir_des
        else:
            return q_goal
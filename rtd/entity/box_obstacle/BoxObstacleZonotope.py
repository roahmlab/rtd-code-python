from rtd.entity.box_obstacle import BoxObstacleInfo
from rtd.entity.components import GenericEntityState
from zonopy import zonotope
import numpy as np
import torch



class BoxObstacleZonotope():
    def __init__(self, box_info: BoxObstacleInfo, box_state: GenericEntityState):
        self.box_info: BoxObstacleInfo = box_info
        self.box_state: GenericEntityState = box_state
        
        self.reset()
    

    def reset(self):
        """
        Resets this component
        """
        center = np.zeros(self.box_info.dimension)
        self.base_zonotope = zonotope(np.vstack([center, np.diag(np.array(self.box_info.dims)/2)]))
        

    def get_zonotope(self, state = None, time: float = None) -> zonotope:
        """
        Returns zonotope of the BoxObstacle. Takes in either a
        state or time.
        
        Parameters
        ----------
        state : list[float]
            state to generate zonotope with
        time : float
            time to generate zonotope with
        """
        if state is None:
            state = self.box_state.get_state(time)
            
        return self.base_zonotope + torch.tensor(state["state"])
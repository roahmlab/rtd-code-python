from trimesh import Trimesh
from rtd.sim.systems.collision import DynamicCollisionObject, CollisionObject
from armour.agent import ArmourAgentInfo, ArmourAgentState
import numpy as np
from collections import OrderedDict
from nptyping import NDArray



class ArmourAgentCollision(DynamicCollisionObject):
    def __init__(self, arm_info: ArmourAgentInfo, arm_state: ArmourAgentState):
        # initialize base classes
        DynamicCollisionObject.__init__(self)
        # initialize
        self.arm_info = arm_info
        self.arm_state = arm_state
        
        # self.reset()
    
    
    def reset(self):
        '''
        Not needed as collision objects are created on demand
        '''
        pass
    
    
    def getCollisionObject(self, q: NDArray = None, time: float = None) -> CollisionObject:
        '''
        Generates a CollisionObject for a given time `time` or
        configuration `q`
        '''
        if q is None:
            q = self.arm_state.position[:,-1]                   # last position
        if time is not None:
            q = self.arm_state.get_state(np.array([time])).q    # position at given time
        config = self.arm_state.get_state(np.array([time])).q
        fk: OrderedDict[Trimesh, NDArray] = self.arm_info.robot.visual_trimesh_fk(cfg=config)
        meshes = [mesh.copy().apply_transform(transform) for mesh, transform in fk.items()]
        return CollisionObject(meshes, id(self.arm_info))       
    
    
    def __str__(self) -> str:
        return (f"Collision component {repr(self)} with properties:\n" + 
                f"   arm_info:  {repr(self.arm_info)}\n" +
                f"   arm_state: {repr(self.arm_state)}\n")  
from trimesh import Trimesh
from rtd.sim.systems.collision import DynamicCollisionObject, CollisionObject
from armour.agent import ArmourAgentInfo, ArmourAgentState
import numpy as np
from collections import OrderedDict
from rtd.util.mixins.Typings import Matnp



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
    
    
    def getCollisionObject(self, q: Matnp = None, time: float = None) -> CollisionObject:
        '''
        Generates a CollisionObject for a given time `time` or
        configuration `q` (only one or none must be provided)
        '''
        config = self.arm_state.position[:,-1]  # default to last position
        if time is None and q is not None:
            config = q
        elif time is not None and q is None:
            config = self.arm_state.get_state(np.array([time])).position   # position at given time
            
        fk: OrderedDict[Trimesh, Matnp] = self.arm_info.robot.collision_trimesh_fk(cfg=config)
        meshes = [mesh.copy().apply_transform(transform) for mesh, transform in fk.items()]
        return CollisionObject(meshes, id(self.arm_info))
    
    
    def __str__(self) -> str:
        return (f"Collision component {repr(self)} with properties:\n" + 
                f"   arm_info:  {repr(self.arm_info)}\n" +
                f"   arm_state: {repr(self.arm_state)}\n")  
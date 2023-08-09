from rtd.sim.systems.patch3d_collision import Patch3dDynamicObject, Patch3dObject
from rtd.entity.box_obstacle import BoxObstacleInfo
from rtd.entity.components import GenericEntityState
from trimesh.primitives import Box



class BoxObstacleCollision(Patch3dDynamicObject):
    def __init__(self, box_info: BoxObstacleInfo, box_state: GenericEntityState):
        # initialize base classes
        Patch3dDynamicObject.__init__(self)
        # initialize
        self.box_info: BoxObstacleInfo = box_info
        self.box_state: GenericEntityState = box_state
        
        self.reset()
    
    
    def reset(self):
        self.mesh = Box(extents=self.box_info.dims).to_mesh()
    
    
    def getCollisionObject(self, time: float = None) -> Patch3dObject:
        '''
        Generates Patch3dObject for a given time `time`
        '''
        transform = self.box_state.get_state(time)["state"]
        mesh = self.mesh.copy().apply_translation(transform)
        
        return Patch3dObject(mesh, id(self.box_info))       
         
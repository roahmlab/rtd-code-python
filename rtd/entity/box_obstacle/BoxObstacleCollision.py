from rtd.sim.systems.collision import DynamicCollisionObject, CollisionObject
from rtd.entity.box_obstacle import BoxObstacleInfo
from rtd.entity.components import GenericEntityState
from trimesh.primitives import Box



class BoxObstacleCollision(DynamicCollisionObject):
    def __init__(self, box_info: BoxObstacleInfo, box_state: GenericEntityState):
        # initialize base classes
        DynamicCollisionObject.__init__(self)
        # initialize
        self.box_info: BoxObstacleInfo = box_info
        self.box_state: GenericEntityState = box_state
        self.mesh = Box(extents=self.box_info.dims).to_mesh()
        
        self.reset()
    
    
    def reset(self):
        self.mesh = Box(extents=self.box_info.dims).to_mesh()
    
    
    def getCollisionObject(self, time: float = None) -> CollisionObject:
        '''
        Generates a CollisionObject for a given time `time`
        '''
        transform = self.box_state.get_state(time)["state"]
        mesh = self.mesh.copy().apply_translation(transform)
        
        return CollisionObject(mesh, id(self.box_info))       
         
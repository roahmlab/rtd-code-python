from rtd.functional.sequences import toSequence
from trimesh import Trimesh
from trimesh.collision import CollisionManager

# type hinting
CollisionPair = tuple[int, int]



class Patch3dObject:
    '''
    A class for storing the mesh of an object to handle its
    collision
    '''
    def __init__(self, meshes: Trimesh | list[Trimesh], parent=None):
        # trimesh.Trimesh object
        self.meshes: list[Trimesh] = toSequence(meshes)
        
        # parent (usually id of info component)
        self.parent: int = parent
        
        # collision handle
        self._collision_handle = CollisionManager()
        for mesh in self.meshes:
            self._collision_handle.add_object(id(mesh), mesh)
    
    
    def inCollision(self, other: 'Patch3dObject') -> tuple[bool, CollisionPair]:
        '''
        Checks if this object is in collision with another object.
        Returns a bool as well as its and its collided pair's
        parent. Note that this should only be used for quick
        collision checks with a single other object
        '''
        # skip collision check if they share the same parent
        if self.parent == other.parent and self.parent is not None:
            return (False, tuple())
        
        # check collision
        collided, _ = self._collision_handle.in_collision_other(other._collision_handle)
        return (True, (self.parent, other.parent)) if collided else (False, tuple())
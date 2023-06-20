import numpy as np
from trimesh import Trimesh
from trimesh.collision import CollisionManager

# type hinting
CollisionPair = tuple['Patch3dObject', 'Patch3dObject']



class Patch3dObject:
    '''
    A class for storing the mesh of an object to handle its
    collision
    '''
    def __init__(self, mesh: Trimesh, parent=None):
        # trimesh.Trimesh object
        self.mesh: Trimesh = mesh
        
        # parent
        self.parent: 'Patch3dObject' = parent
        
        # collision handle
        self._collision_handle = CollisionManager()
        self._collision_handle.add_object(id(mesh), self.mesh)
    
    
    def inCollision(self, other: 'Patch3dObject') -> tuple[bool, CollisionPair]:
        '''
        Checks if this object is in collision with another object.
        Returns a bool as well as its and its collided pair's
        parent. Note that this should only be used for quick
        collision checks with a single other object
        '''
        # skip collision check if they share the same parent
        if self.parent == other.parent and self.parent != None:
            return (False, tuple())
        
        # check collision
        collided = self._collision_handle.in_collision_other(other._collision_handle)
        return (collided, (self.parent, other.parent)) if collided else (collided, tuple())
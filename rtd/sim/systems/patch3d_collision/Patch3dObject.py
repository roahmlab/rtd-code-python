import numpy as np
from trimesh.collision import CollisionManager



class Patch3dObject:
    '''
    A class for storing the mesh of a 3d
    object to handle an object's collision
    '''
    def __init__(self):
        # a trimesh object
        self.mesh = None
        # parent
        self.parent = None
    
    
    def inCollision(self, other) -> tuple[bool, tuple]:
        '''
        Checks if this object's mesh is in 
        collision with another object's mesh
        '''
        # skip collision check if they share the same parent
        if id(self.parent) == id(other.parent):
            return (False, tuple())
        
        # do a fast axis-aligned bbox check first
        # and skip collision check if bbox don't
        # intersect
        min1, max1 = self.mesh.bounds
        min2, max2 = other.mesh.bounds
        if np.any(min1 > max2) or np.any(min2 > max1):
            return (False, tuple())
        
        # if bbox intersects, do thorough collision check
        # NOTE: trimesh.collision may already do this
        # will have to look into the source code to see
        # also probably more optimized to do the collision
        # with all the objects at once, rather than using
        # the inCollision command
        manager = CollisionManager()
        manager.add_object("self", self.mesh)
        manager.add_object("other", other.mesh)
        col = manager.in_collision_internal()
        
        if col:
            return (True, (self, other))
        return (False, tuple())
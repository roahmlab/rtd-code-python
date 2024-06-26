from __future__ import annotations
from typing import TYPE_CHECKING
from rtd.functional.sequences import toSequence
from trimesh.collision import CollisionManager

if TYPE_CHECKING:
    from trimesh import Trimesh

# type hinting
CollisionPair = tuple[int, int]



class CollisionObject:
    '''
    A class for storing the mesh of an object to handle its
    collision
    '''
    def __init__(self, meshes: Trimesh | list[Trimesh], parent: int = None):
        # trimesh.Trimesh object
        self.meshes: list[Trimesh] = toSequence(meshes)
        
        # parent (usually id of info component)
        self.parent: int = parent
        
        # collision handle
        self._collision_handle = CollisionManager()
        for mesh in self.meshes:
            self._collision_handle.add_object(id(mesh), mesh)
    
    
    def inCollision(self, other: 'CollisionObject') -> tuple[bool, CollisionPair]:
        '''
        Checks if this object is in collision with another object.
        Returns a bool as well as its and its collided pair's
        parent. Note that this should only be used for quick
        collision checks with a single other object
        
        Parameters
        ----------
        other : CollisionObject
            the object to check collision against
        
        Returns
        -------
        collided: bool
            whether self is in collision with other
        pair : tuple[int, int]
            pair of self.parent and other.parent
        '''
        # skip collision check if they share the same parent
        if self.parent == other.parent and self.parent is not None:
            return (False, tuple())
        
        # check collision
        collided = self._collision_handle.in_collision_other(other._collision_handle)
        return (True, (self.parent, other.parent)) if collided else (False, tuple())
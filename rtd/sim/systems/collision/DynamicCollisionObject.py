from abc import ABCMeta, abstractmethod
from rtd.sim.systems.collision import CollisionObject



class DynamicCollisionObject(metaclass=ABCMeta):
    '''
    Base class for generating a CollisionObject of
    a dynamic object at a specified time
    '''
    @abstractmethod
    def getCollisionObject(self, **options) -> CollisionObject:
        '''
        Abstract method which needs to be implemented
        to return a CollisionObject with mesh at a given
        time (and any other options)
        '''
        pass
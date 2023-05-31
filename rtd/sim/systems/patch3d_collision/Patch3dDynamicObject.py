from abc import ABCMeta, abstractmethod



class Patch3dDynamicObject(metaclass=ABCMeta):
    '''
    Base class for generating a Patch3dObject of
    a dynamic object at a specified time
    '''
    @abstractmethod
    def getCollisionObject(self, **options):
        '''
        Abstract method which needs to be implemented
        to return a Patch3dObject with mesh at a given
        time (and any other options)
        '''
        pass
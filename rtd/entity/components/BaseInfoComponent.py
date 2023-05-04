from abc import ABCMeta, abstractmethod



class BaseInfoComponent(metaclass=ABCMeta):
    '''
    Base class for storing immutable parameters tied
    to an entity. Should be extended along with the 
    `Options` mixin to add specific properties
    '''
    def __init__(self):
        # Number of dimensions. Should be 2 or 3
        self.dimension = None
    

    @abstractmethod
    def reset(self):
        '''
        Abstract method which needs to be implemented
        to reset each property
        '''
        pass
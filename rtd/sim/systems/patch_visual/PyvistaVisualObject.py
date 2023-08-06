from abc import ABCMeta, abstractmethod
from pyvista import Actor



class PyvistaVisualObject(metaclass=ABCMeta):
    '''
    An object that can be extended to control the
    rendering of an entity
    '''
    @abstractmethod
    def plot(self, **options) -> Actor:
        '''
        Abstract method which needs to be implemented to update
        the current plot_data and returns a pyvista actor
        object, which can be added to the current plot through
        the `add_actor` method of the plotter
        '''
        pass
    
    
    def __init__(self):
        # a pyvista actor object
        self.plot_data: Actor = None
    
    
    def isPlotDataValid(self):
        '''
        Checks if plot_data is a pyvista actor object
        '''
        return issubclass(type(self.plot_data), Actor)
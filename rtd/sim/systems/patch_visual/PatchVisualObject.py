from abc import ABCMeta, abstractmethod
from matplotlib import artist



class PatchVisualObject(metaclass=ABCMeta):
    '''
    An object that can be extended to control the
    rendering of an entity
    '''
    @abstractmethod
    def plot(self, **options) -> artist:
        '''
        Abstract method which needs to be implemented to update
        the current plot_data and returns a matplotlib artist
        object, which can be added to the current figure through
        the `add_artist` method of the figure axes
        '''
        pass
    
    
    def __init__(self):
        # a matplotlib artist object
        self.plot_data: artist = None
    
    
    def isPlotDataValid(self):
        '''
        Checks if plot_data is a matplotlib artist object
        '''
        return issubclass(type(self.plot_data), artist)
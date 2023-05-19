from abc import ABCMeta, abstractmethod



class PatchVisualObject(metaclass=ABCMeta):
    '''
    An object that can be extended to control the
    rendering of an entity
    '''
    @abstractmethod
    def get_plot_data(self, **options):
        '''
        Abstract method which needs to be implemented to return
        a matplotlib artist object, which can be plotted through
        the `add_artist` method of the figure axes
        '''
        pass
    
    
    def __init__(self):
        # a matplotlib artist object
        plot_data = None
    
    
    def isPlotDataValid(self, fieldname: str):
        return NotImplementedError
from abc import ABCMeta, abstractmethod
from rtd.functional.sequences import toSequence
from trimesh import Trimesh
from nptyping import NDArray



class ClientVisualObject(metaclass=ABCMeta):
    '''
    An object that can be extended to control the
    rendering of an entity
    '''
    @abstractmethod
    def create_plot_data(self, **options) -> Trimesh | list[Trimesh]:
        '''
        Abstract method which needs to be implemented to generate
        and return the plot data
        
        Parameters
        ----------
        **options
            options for creating the plot data
        
        Returns
        -------
        plot_obj : Trimesh | list[Trimesh]
            Trimesh mesh(es) to plot
        '''
        pass

    
    @abstractmethod
    def plot(self, **options) -> NDArray:
        '''
        Abstract method which needs to be implemented to return
        the transformation matrices for the plot_data animation
        '''
        pass
    
    
    def __init__(self):
        # trimesh mesh(es)
        self.plot_data: Trimesh | list[Trimesh] = None
    
    
    def isPlotDataValid(self) -> bool:
        '''
        Checks if plot_data is a Trimesh mesh
        
        Returns
        -------
        is_valid : bool
            whether the plot_data is a valid Trimesh mesh
        '''
        return issubclass(type(toSequence(self.plot_data)[0]), Trimesh)
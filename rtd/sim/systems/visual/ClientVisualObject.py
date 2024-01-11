from abc import ABCMeta, abstractmethod
from rtd.functional.sequences import toSequence
from rtd.sim.websocket import MeshData

# for type hinting
MoveMsg = tuple[str, dict, dict]



class ClientVisualObject(metaclass=ABCMeta):
    '''
    An object that can be extended to control the
    rendering of an entity
    '''
    @abstractmethod
    def create_plot_data(self, **options) -> MeshData | list[MeshData]:
        '''
        Abstract method which needs to be implemented to initialize
        self.plot_data to a Trimesh mesh (or a list of meshes), and
        return the corresponding MeshData(s)
        
        Parameters
        ----------
        **options
            options for creating the plot data
        
        Returns
        -------
        plot_obj : MeshData | list[MeshData]
            Websocket MeshData(s) to plot
        '''
        pass

    
    @abstractmethod
    def plot(self, **options) -> MoveMsg | list[MoveMsg]:
        '''
        Abstract method which needs to be implemented to return
        the transformation and rotation matrices for the plot_data
        animation
        
        Returns
        _______
        move_msg : MoveMsg | list[MoveMsg]
            a tuple of mesh guid, transformation matrix,
            and rotation matrix for every object in plot_data
        '''
        pass
    
    
    def __init__(self):
        # trimesh mesh(es)
        self.plot_data: MeshData | list[MeshData] = None
    
    
    def isPlotDataValid(self) -> bool:
        '''
        Checks if plot_data is a Trimesh mesh
        
        Returns
        -------
        is_valid : bool
            whether the plot_data is a valid Trimesh mesh
        '''
        return issubclass(type(toSequence(self.plot_data)[0]), MeshData)
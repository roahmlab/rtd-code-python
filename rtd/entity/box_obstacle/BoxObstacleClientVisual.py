from rtd.sim.systems.visual import ClientVisualObject, MoveMsg
from rtd.util.mixins import Options
from rtd.entity.box_obstacle import BoxObstacleInfo
from rtd.entity.components import GenericEntityState
from rtd.sim.websocket import MeshData
import uuid
import trimesh



class BoxObstacleClientVisual(ClientVisualObject, Options):
    '''
    A visual component used to generate the plot data of
    the box obstacle
    '''
    @staticmethod
    def defaultoptions() -> dict:
        """
        Default options for the BoxObstacleVisual
        """
        return {
            "face_color": [1.0, 0.0, 1.0],
            "face_opacity": 0.2,
            "edge_color": [0.0, 0.0, 0.0],
            "edge_width": 1,
        }

    
    def __init__(self, box_info: BoxObstacleInfo, box_state: GenericEntityState, **options):
        # initialize base classes
        ClientVisualObject.__init__(self)
        Options.__init__(self)
        # initialize using given options
        options["face_color"] = box_info.color
        self.mergeoptions(options)
        
        self.box_info: BoxObstacleInfo = box_info
        self.box_state: GenericEntityState = box_state
        
        self.reset()
    
    
    def reset(self, **options):
        """
        Resets this component
        """
        options = self.mergeoptions(options)
        self.face_color = options["face_color"]
        self.face_opacity = options["face_opacity"]
        self.edge_color = options["edge_color"]
        self.edge_width = options["edge_width"]
        self.create_plot_data()
    
    
    def create_plot_data(self, **options) -> MeshData:
        """
        Generates the initial plot data
        
        Returns
        _______
        plot_data : MeshData
            MeshData to plot
        """
        
        xw, yw, zw = self.box_info.dims
        mesh = trimesh.primitives.Box((xw, yw, zw))
        mesh_data = MeshData.from_trimesh(mesh)
        mesh_data.Color = [self.face_color[0], self.face_color[1], self.face_color[2], self.face_opacity]
        self.plot_data = mesh_data
        
        return self.plot_data
    
    
    def plot(self, time: float = None) -> MoveMsg:
        """
        Updates the plotdata of the BoxObstalce
        
        Parameters
        ----------
        time : float
            time of plot data
        """
        if time is None:
            time = self.box_state.time[-1]

        x, y, z = self.box_state.get_state(time)["state"]
        position = (x, y, z)
        rotation = (0.0, 0.0, 0.0)
        return (
            self.plot_data.GUID,
            position, rotation
        )


    def __str__(self) -> str:
        return (f"{repr(self)} with properties:\n" + 
                f"   box_info:  {repr(self.box_info)}\n"
                f"   box_state: {repr(self.box_state)}\n")
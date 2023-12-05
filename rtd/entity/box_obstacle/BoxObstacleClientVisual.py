from rtd.sim.systems.visual import ClientVisualObject
from rtd.util.mixins import Options
from rtd.entity.box_obstacle import BoxObstacleInfo
from rtd.entity.components import GenericEntityState
from rtd.sim.websocket import MeshData
import uuid

# for type hinting
MoveMsg = tuple[str, dict, dict]



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
        self.plot_data: MeshData = MeshData()
        self.plot_data.Vertices = [
            # front face
            -xw/2, -yw/2,  zw/2,    # bottom left
             xw/2, -yw/2,  zw/2,    # bottom right
             xw/2,  yw/2,  zw/2,    # top right
            -xw/2,  yw/2,  zw/2,    # top left
            # back face
            -xw/2, -yw/2, -zw/2,
             xw/2, -yw/2, -zw/2,
             xw/2,  yw/2, -zw/2,
            -xw/2,  yw/2, -zw/2, 
        ]
        self.plot_data.Color = self.face_color * 8
        self.plot_data.UV0 = [0.0, 0.0] * 8
        self.plot_data.UV1 = [0.0, 0.0] * 8
        self.plot_data.IndicesData = [
            0, 1, 2, 2, 3, 0,   # front
            1, 5, 6, 6, 2, 1,   # right
            7, 6, 5, 5, 4, 7,   # back
            4, 0, 3, 3, 7, 4,   # left
            4, 5, 1, 1, 0, 4,   # bottom
            3, 2, 6, 6, 7, 3,   # top            
        ]
        self.plot_data.VerticesCount = 8
        self.plot_data.IndicesCount = 12
        self.plot_data.GUID = str(uuid.uuid4())
        
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
        return (
            self.plot_data.GUID,
            {'x': x, 'y': y, 'z': z},
            {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 0.0}
        )


    def __str__(self) -> str:
        return (f"{repr(self)} with properties:\n" + 
                f"   box_info:  {repr(self.box_info)}\n"
                f"   box_state: {repr(self.box_state)}\n")
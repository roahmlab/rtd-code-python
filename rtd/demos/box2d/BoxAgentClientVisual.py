from rtd.sim.systems.visual import ClientVisualObject, MoveMsg
from rtd.util.mixins import Options
from rtd.demos.box2d import BoxAgentInfo
from rtd.entity.components import GenericEntityState
from rtd.sim.websocket import MeshData
import trimesh



class BoxAgentClientVisual(ClientVisualObject, Options):
    '''
    A visual component used to generate the plot data of
    the box agent
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "face_color": [1.0, 0.0, 1.0],
            "face_opacity": 0.2,
            "edge_color": [0.0, 0.0, 0.0],
            "edge_width": 1,
        }

    
    def __init__(self, box_info: BoxAgentInfo, box_state: GenericEntityState, **options):
        # initialize base classes
        ClientVisualObject.__init__(self)
        Options.__init__(self)
        # initialize using given options
        options["face_color"] = box_info.color
        self.mergeoptions(options)
        
        self.box_info: BoxAgentInfo = box_info
        self.box_state: GenericEntityState = box_state
        
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.face_color = options["face_color"]
        self.face_opacity = options["face_opacity"]
        self.edge_color = options["edge_color"]
        self.edge_width = options["edge_width"]
        self.create_plot_data()
    
    
    def create_plot_data(self, time: float = None) -> MeshData:
        if time is None:
            time = self.box_state.time[-1]
            
        w = self.box_info.width
        h = self.box_info.height
        
        mesh = trimesh.primitives.Box((w, h, 0.01))
        mesh_data = MeshData.from_trimesh(mesh)
        mesh_data.Color = [self.face_color[0], self.face_color[1], self.face_color[2], self.face_opacity]

        # # set coordinate of rectangle to draw
        # x, y = self.box_state.get_state(time)["state"]
        # mesh_data.position['x'] = x
        # mesh_data.position['y'] = y

        self.plot_data = mesh_data
        
        return self.plot_data
    
    
    def plot(self, time: float = None) -> MoveMsg:
        if time is None:
            time = self.box_state.time[-1]

        # set coordinate of rectangle to draw
        x, y = self.box_state.get_state(time)["state"]
        position = (x, y, 0.0)
        rotation = (0.0, 0.0, 0.0)
        return (self.plot_data.GUID, position, rotation)


    def __str__(self) -> str:
        return (f"{repr(self)} with properties:\n" + 
                f"   box_info:  {repr(self.box_info)}\n"
                f"   box_state: {repr(self.box_state)}\n")
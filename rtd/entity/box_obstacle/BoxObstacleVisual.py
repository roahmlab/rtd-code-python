from rtd.sim.systems.visual import PyvistaVisualObject
from rtd.util.mixins import Options
from rtd.entity.box_obstacle import BoxObstacleInfo
from rtd.entity.components import GenericEntityState
from pyvista import Actor
import pyvista as pv



class BoxObstacleVisual(PyvistaVisualObject, Options):
    '''
    A visual component used to generate the plot data of
    the box obstacle
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "face_color": [1.0, 0.0, 1.0],
            "face_opacity": 0.2,
            "edge_color": [0.0, 0.0, 0.0],
            "edge_width": 1,
        }

    
    def __init__(self, box_info: BoxObstacleInfo, box_state: GenericEntityState, **options):
        # initialize base classes
        PyvistaVisualObject.__init__(self)
        Options.__init__(self)
        # initialize using given options
        options["face_color"] = box_info.color
        self.mergeoptions(options)
        
        self.box_info: BoxObstacleInfo = box_info
        self.box_state: GenericEntityState = box_state
        
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.face_color = options["face_color"]
        self.face_opacity = options["face_opacity"]
        self.edge_color = options["edge_color"]
        self.edge_width = options["edge_width"]
        self.create_plot_data()
    
    
    def create_plot_data(self, time: float = None) -> Actor:
        if time is None:
            time = self.box_state.time[-1]
        
        xw, yw, zw = self.box_info.dims
        mesh = pv.Box([0, xw, 0, yw, 0, zw])
        mapper = pv.DataSetMapper(mesh)
        self.plot_data = pv.Actor(mapper=mapper)
        
        # set properties
        self.plot_data.prop.SetColor(*self.face_color)
        self.plot_data.prop.SetOpacity(self.face_opacity)
        if self.edge_width > 0:
            self.plot_data.prop.EdgeVisibilityOn()
            self.plot_data.prop.SetLineWidth(self.edge_width)
            self.plot_data.prop.SetEdgeColor(*self.edge_color)
        
        # set coordinate of rectangle to draw
        x, y, z = self.box_state.get_state(time)["state"]
        self.plot_data.SetPosition(x, y, z)
        
        return self.plot_data
    
    
    def plot(self, time: float = None):
        if time is None:
            time = self.box_state.time[-1]

        # set coordinate of box to draw
        x, y, z = self.box_state.get_state(time)["state"]
        self.plot_data.SetPosition(x, y, z)


    def __str__(self) -> str:
        return (f"{repr(self)} with properties:\n" + 
                f"   box_info:  {repr(self.box_info)}\n"
                f"   box_state: {repr(self.box_state)}\n")
from rtd.sim.systems.patch_visual import PatchVisualObject
from rtd.util.mixins import Options
import matplotlib
from matplotlib.patches import Rectangle
import numpy as np



class BoxAgentVisual(PatchVisualObject, Options):
    '''
    A visual component used to generate the plot data of
    the box agent
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "face_color": [1, 0, 1],
            "face_opacity": 0.2,
            "edge_color": [0, 0, 0],
            "edge_width": 1,
        }

    
    def __init__(self, box_info, box_state, **options):
        # initialize base classes
        PatchVisualObject.__init__(self)
        Options.__init__(self)
        # initialize using given options
        options["face_color"] = box_info.color
        self.mergeoptions(options)
        
        self.box_info = box_info
        self.box_state = box_state
        
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.face_color = options["face_color"]
        self.face_opacity = options["face_opacity"]
        self.edge_color = options["edge_color"]
        self.edge_width = options["edge_width"]
        self.create_plot_data()
    
    
    def create_plot_data(self):
        '''
        Creates a matplotlib artist object and saves it
        as `self.plot_data`. It's starting position is
        (0, 0)
        '''
        w = self.box_info.width
        h = self.box_info.height
        options = self.getoptions()
        
        self.plot_data = Rectangle((0, 0), w, h,
            facecolor=self.face_color,
            alpha=self.face_opacity,
            edgecolor=self.edge_color,
            linewidth=self.edge_width,
        )
    
    
    def plot(self, time: float = None) -> matplotlib.artist:
        '''
        Sets the anchor point of `self.plot_data` to the
        state at the given time and returns the plot data.
        The plot data can be added to the current figure by
        using the `add_artist` method of the figure axes
        '''
        if time == None:
            time = self.box_state.time[-1]

        # set coordinate of rectangle to draw
        self.plot_data.xy = self.box_state.get_state(time)["state"]
        
        return self.plot_data


    def __str__(self) -> str:
        return (f"{repr(self)} with properties:\n" + 
                f"   box_info:  {repr(self.box_info)}\n"
                f"   box_state: {repr(self.box_state)}\n")
from rtd.sim.systems.visual import PyvistaVisualObject
from rtd.util.mixins import Options
from armour.agent import ArmourAgentInfo, ArmourAgentState
from pyvista import Actor
import pyvista as pv
import numpy as np
from trimesh import Trimesh
from typing import OrderedDict
from rtd.util.mixins.Typings import Matnp


class ArmourAgentVisual(PyvistaVisualObject, Options):
    '''
    A visual component used to generate the plot data of
    the Armour agent
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "face_color": [0.8, 0.8, 1],
            "face_opacity": 1,
            "edge_color": [0, 0, 1],
            "edge_width": 1,
        }

    
    def __init__(self, arm_info: ArmourAgentInfo, arm_state: ArmourAgentState, **options):
        # initialize base classes
        PyvistaVisualObject.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        
        self.arm_info: ArmourAgentInfo = arm_info
        self.arm_state: ArmourAgentState = arm_state
        
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.face_color = options["face_color"]
        self.face_opacity = options["face_opacity"]
        self.edge_color = options["edge_color"]
        self.edge_width = options["edge_width"]
    
    
    def create_plot_data(self, time: float = None) -> list[Actor]:
        '''
        Generate the trimesh meshes at the given time and
        converts them into actors
        '''
        if time is None:
            time = self.box_state.time[-1]

        # generate mesh
        config = self.arm_state.get_state(np.array([time])).position
        fk: OrderedDict[Trimesh, Matnp] = self.arm_info.urdf.visual_trimesh_fk(cfg=config)
        meshes = [mesh.copy().apply_transform(transform) for mesh, transform in fk.items()]
        
        self.plot_data: list[Actor] = list()
        
        # generate actors from mesh
        for mesh in meshes:
            mesh = pv.wrap(mesh)
            mapper = pv.DataSetMapper(mesh)
            self.plot_data.append(pv.Actor(mapper=mapper))
            
            # set properties
            self.plot_data[-1].prop.SetColor(*self.face_color)
            self.plot_data[-1].prop.SetOpacity(self.face_opacity)
            if self.edge_width > 0:
                self.plot_data[-1].prop.EdgeVisibilityOn()
                self.plot_data[-1].prop.SetLineWidth(self.edge_width)
                self.plot_data[-1].prop.SetEdgeColor(*self.edge_color)
        
        return self.plot_data
    
    
    def plot(self, time: float = None):
        '''
        Replaces the mesh of the actors to update their pose
        '''
        if time is None:
            time = self.box_state.time[-1]

        # generate mesh
        config = self.arm_state.get_state(np.array([time])).position
        fk: OrderedDict[Trimesh, Matnp] = self.arm_info.urdf.visual_trimesh_fk(cfg=config)
        meshes = [mesh.copy().apply_transform(transform) for mesh, transform in fk.items()]

        for actor, mesh in zip(self.plot_data, meshes):
            # replace mesh of actor with new mesh
            mesh = pv.wrap(mesh)
            mapper = pv.DataSetMapper(mesh)
            actor.SetMapper(mapper)
            

    def __str__(self) -> str:
        return (f"Visual component {repr(self)} with properties:\n" + 
                f"   arm_info:  {repr(self.arm_info)}\n" +
                f"   arm_state: {repr(self.arm_state)}\n")
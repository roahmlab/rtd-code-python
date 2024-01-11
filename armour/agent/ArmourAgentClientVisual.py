from rtd.sim.systems.visual import ClientVisualObject, MoveMsg
from rtd.util.mixins import Options
from armour.agent import ArmourAgentInfo, ArmourAgentState
from pyvista import Actor
import pyvista as pv
import numpy as np
from trimesh import Trimesh
from typing import OrderedDict
from rtd.util.mixins.Typings import Matnp
from rtd.sim.websocket import MeshData
from scipy.spatial.transform import Rotation as R


class ArmourAgentClientVisual(ClientVisualObject, Options):
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
        ClientVisualObject.__init__(self)
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
    
    
    def create_plot_data(self, time: float = None) -> list[MeshData]:
        '''
        Generate the trimesh meshes at the given time and
        converts them into actors
        '''
        if time is None:
            time = self.arm_state.time[-1]

        # generate mesh
        config = self.arm_state.get_state(np.array([time])).position
        fk: OrderedDict[Trimesh, Matnp] = self.arm_info.urdf.visual_trimesh_fk(cfg=config)
        # meshes = [mesh.copy().apply_transform(transform) for mesh, transform in fk.items()]
        self.mesh_datas: dict[Trimesh, MeshData] = {mesh: MeshData.from_trimesh(mesh) for mesh in fk.keys()}
        # add color
        for mesh_data in self.mesh_datas.values():
            mesh_data.Color = [self.face_color[0], self.face_color[1], self.face_color[2], self.face_opacity]
        
        self.plot_data: list[MeshData] = list(self.mesh_datas.values())
        
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

        # Generate the position and rotation of the meshs
        msg_list = []
        for mesh, transform in fk.items():
            # Get the position and rotation of the mesh
            position = transform[:3, 3]
            rotation = R.from_matrix(transform[:3, :3]).as_euler('xyz', degrees=True)
            # Get the mesh data
            guid = self.mesh_datas[mesh].GUID
            # Update the plot data
            msg_list.append((guid, tuple(position), tuple(rotation)))
        return msg_list
            

    def __str__(self) -> str:
        return (f"Visual component {repr(self)} with properties:\n" + 
                f"   arm_info:  {repr(self.arm_info)}\n" +
                f"   arm_state: {repr(self.arm_state)}\n")
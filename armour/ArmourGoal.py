from rtd.sim.systems.visual import PyvistaVisualObject
from rtd.sim.systems.collision import TrimeshCollisionSystem
from armour import ArmourAgent
from rtd.functional.sequences import arrange_list
from rtd.util.mixins import Options
from pyvista import Actor
import pyvista as pv
import numpy as np
from trimesh import Trimesh
from typing import OrderedDict
from math import pi
from rtd.util.mixins.Typings import Matnp

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ArmourGoal(PyvistaVisualObject, Options):
    @staticmethod
    def defaultoptions() -> dict:
        return {
            'time_discretization': 0.1,
            'face_color': [0, 1, 0],
            'face_opacity': 0.1,
            'edge_color': [0, 1, 0],
            'edge_width': 1,
            'start_position': None,
            'goal_position': None,
            'min_dist_start_to_goal': None,
            'goal_creation_timeout': 10,
            'goal_radius': pi/30,
        }
    
    
    def __init__(self, collision_system: TrimeshCollisionSystem, arm_agent: ArmourAgent, **options):
        '''
        Initialize the goal position
        '''
        # initialize base classes
        PyvistaVisualObject.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        
        self.collision_system: TrimeshCollisionSystem = collision_system
        self.arm_agent: ArmourAgent = arm_agent
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.time: list[float] = [0]
        self.time_discretization: float = options["time_discretization"]
        self.face_color = options["face_color"]
        self.face_opacity = options["face_opacity"]
        self.edge_color = options["edge_color"]
        self.edge_width = options["edge_width"]
        self.start_position = options["start_position"]
        self.goal_position = options["goal_position"]
        self.min_dist_start_to_goal = options["min_dist_start_to_goal"]
        self.goal_creation_timeout = options["goal_creation_timeout"]
        self.goal_radius = options["goal_radius"]
        
        if self.start_position is None:
            self.start_position = self.arm_agent.state.get_state().position
            
        if self.min_dist_start_to_goal is None:
            # TODO calculate max range and set min distance to 0.25 times of that
            self.min_dist_start_to_goal = 0
            
        if self.goal_position is None:
            self.random_init()
        
        self.create_plot_data()
    
    
    def create_plot_data(self, time: float = None) -> list[Actor]:
        # generate mesh
        config = self.goal_position
        fk: OrderedDict[Trimesh, Matnp] = self.arm_agent.info.robot.visual_trimesh_fk(cfg=config)
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
        Goal doesn't change
        '''
        pass
    
    
    def random_init(self):
        '''
        Generates a random goal with dist > min_dist
        untils there are no collision or it times out
        '''
        return NotImplementedError
    
    
    def updateGoal(self, t_update: float = None) -> bool:
        '''
        Updates the goal and returns true if the goal
        is reached
        '''
        start_time = self.time[-1] + self.time_discretization
        end_time = self.time[-1] + t_update + self.time_discretization
        t_vec = arrange_list(start_time, end_time, self.time_discretization)
        
        logger.debug("Running the goal check!")
        
        # accumulate the return
        goal = False
        get_pos = lambda t : self.arm_agent.state.get_state(t).position
        for t_check in t_vec:
            goal |= np.all(np.abs(get_pos(t_check) - self.goal_position) <= self.goal_radius, axis=None)
        
        self.time += t_vec
        return goal
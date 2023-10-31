from rtd.sim import BaseSimulation
from rtd.sim.types import SimulationState
from rtd.sim.systems.collision import TrimeshCollisionSystem, DynamicCollisionObject, CollisionObject
from rtd.sim.systems.visual import PyvistaVisualSystem, PyvistaVisualObject
from rtd.entity.box_obstacle import BoxObstacle
from armour import ArmourAgent, ArmourGoal
import numpy as np
from typing import Callable

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ArmourSimulation(BaseSimulation):
    def __init__(self, simulate_timestep: float = 0.5):
        # initialize base classes
        BaseSimulation.__init__(self)
        # initialize rest
        self.simulation_timestep = simulate_timestep
        self.world: dict = dict()
        self.entities: list = list()
        self.agent: ArmourAgent = None
        self.obstacles = list()
        self.collision_system: TrimeshCollisionSystem = None
        self.visual_system: PyvistaVisualSystem = None
        self.goal_system = None
        self.simulation_state = SimulationState.CONSTRUCTED
    
    
    def add_object(self, object, isentity: bool = False,
                   collision: CollisionObject | DynamicCollisionObject = None,
                   visual: PyvistaVisualObject = None):
        """
        Add the specified object to the world.
        If it is an entity, it is treated as dynamic.
        
        Parameters
        ----------
        object : Any
            the object to add
        isentity : bool
            whether it is a dynamic entity
        collision : CollisionObject | DynamicCollisionObject
            collision handler of the object
        visual : PyvistaVisualObject
            visual handler of the object
        """
        # Add the object to the world
        # Create a name for the object based on its classname if it
        # doesn't have a given name.
        self.world[id(object)] = object
        
        # Add to the entity list if it's an entity
        if isentity:
            self.entities.append(object)
            # Add the collision component provided to the collision system
            if collision is not None:
                self.collision_system.addObjects(dynamic=collision)

            # Add the visualization component provided to the visual
            # system
            if visual is not None:
                self.visual_system.addObjects(dynamic=visual)
        
        # if it's not, check for and add to collision or visual
        else:
            if collision is not None:
                self.collision_system.addObjects(static=collision)

            # Add the visualization component provided to the visual
            # system
            if visual is not None:
                self.visual_system.addObjects(static=visual)

        # TODO setup custom event data to return the object added
    
    
    def setup(self, agent: ArmourAgent):
        """
        Populate the world with the ArmourAgent
        
        Parameters
        ----------
        agent : ArmourAgent
            agent to add
        """
        if self.simulation_state > SimulationState.SETTING_UP:
            self.world = dict()
            self.entities = list()
        self.simulation_state = SimulationState.SETTING_UP
        
        self.agent = agent
        # initialize visual and collision
        self.visual_system = PyvistaVisualSystem()
        self.collision_system = TrimeshCollisionSystem()
        
        # add the agent
        self.add_object(agent, isentity=True, collision=agent.collision, visual=agent.visual)
        
        self.simulation_state = SimulationState.SETUP_READY
    
    
    def initialize(self):
        '''
        Initializes the agent, goal, and obstacles
        '''
        if self.simulation_state > SimulationState.INITIALIZING:
            pass
        self.simulation_state = SimulationState.INITIALIZING
        
        # initialize agent state
        self.agent.state.reset(initial_position=np.array([0,-np.pi/2,0,0,0,0,0]).reshape(-1, 1))
        
        # create obstacles
        n_obstacles = 3
        centers = [(-0.0584, 0.2333, 0.2826), (-0.4013, 0.1591, 0.4021), (0.2391, -0.1884, 0.2953)]
        side_lengths = [(0.3915, 0.0572, 0.1350), (0.1760, 0.3089, 0.1013), (0.1545, 0.2983, 0.0352)]
        
        # place obstacles
        for obs_i in range(n_obstacles):
            prop_obs = BoxObstacle.make_box(centers[obs_i], side_lengths[obs_i])
            prop_col: CollisionObject = prop_obs.collision.getCollisionObject(0)
            
            # make sure it doesn't collide
            if not self.collision_system.checkCollisionObject(prop_col)["collided"]:
                self.obstacles.append(prop_obs)
                self.add_object(prop_obs, collision=prop_col, visual=prop_obs.visual)
        
        # add the goal
        goal_position = [2.19112372555967,0.393795848789382,-2.08886547149797,-1.94078143810946,-1.82357815033695,-1.80997964933365,2.12483409695310]
        self.goal_system = ArmourGoal(self.collision_system, self.agent, goal_position=goal_position)
        self.visual_system.addObjects(static=self.goal_system)
        
        override_options = self.agent.get_componentOverrideOptions({'state': self.agent.state})
        self.agent.reset(**override_options)
        self.visual_system.redraw()
        self.simulation_state = SimulationState.READY
    
    
    def pre_step(self) -> dict:
        self.simulation_state = SimulationState.PRE_STEP
        return dict()
    
    
    def step(self) -> dict:
        self.simulation_state = SimulationState.STEP
        
        # update entries
        agent_results = self.agent.update(self.simulation_timestep)
        
        collided, contactedPairs = self.collision_system.updateCollision(self.simulation_timestep)
        
        if collided:
            logger.error("Collision Detected, Breakpoint!")
            input("Press Enter to Unpause")
        
        return {
            "agent_results": agent_results,
            "collided": collided,
            "contactPairs": contactedPairs,
        }
    
    
    def post_step(self) -> dict:
        self.simulation_state
        goal = self.goal_system.updateGoal(self.simulation_timestep)
        self.visual_system.updateVisual(self.simulation_timestep)
        return {
            "goal": goal,
        }
    
    
    def summary(self, **options):
        # does nothing
        return
    
    
    def run(self, max_steps: int = 1e8, pre_step_callback: Callable = None, step_callback: Callable = None,
            post_step_callback: Callable = None, stop_on_goal: bool = True):
        """
        Runs the lifecycle of the simulation
        
        Parameters
        ----------
        max_steps : int
            maximum number of steps to run for
        pre_step_callback : Callable
            function to run before the pre_step
        step_callback : Callable
            function to run before the step
        post_step_callback : Callable
            function to run before the post_step
        stop_on_goal : bool
            whether to stop the simulation once it reaches the goal
        """
        # build the execution order
        execution_queue = [ArmourSimulation.pre_step]
        if pre_step_callback is not None:
            execution_queue.append(pre_step_callback)
        execution_queue.append(ArmourSimulation.step)
        if step_callback is not None:
            execution_queue.append(step_callback)
        execution_queue.append(ArmourSimulation.post_step)
        if post_step_callback is not None:
            execution_queue.append(post_step_callback)
        
        steps = 0
        stop = False
        
        while steps<max_steps and not stop:
            for fcn in execution_queue:
                info = fcn(self)
                # automate logging here
                stop = True if ("stop" in info and info.stop) else False
                if stop_on_goal and "goal" in info and info["goal"]:
                    stop = True
                    print("Goal acheived!")
                # TODO pause on request with keyboard
                
            steps += 1
from rtd.util.mixins import Options
from rtd.sim import ClientSimulationSystem
from rtd.sim.systems.visual import ClientVisualObject
from rtd.functional.sequences import toSequence, arrange
from datetime import datetime
import numpy as np
import time

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ClientVisualSystem(ClientSimulationSystem, Options):
    '''
    Takes in a list of static and dynamic objects and handles
    their rendering
    '''
    @staticmethod
    def defaultoptions() -> dict:
        """
        Returns
        -------
        options : dict
            default options of visual system
        """
        return {
            "time_discretization": 0.1,
            "draw_time": 0.05,
            "dimension": 3,
        }
    
    
    def __init__(self,
                 static_objects: ClientVisualObject | list[ClientVisualObject] = None,
                 dynamic_objects: ClientVisualObject | list[ClientVisualObject] = None,
                 **options):
        # initialize base classes
        ClientSimulationSystem.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.reset()
        self.addObjects(static=static_objects, dynamic=dynamic_objects)
    
    
    def reset(self, **options):
        ClientSimulationSystem.reset(self)
        options = self.mergeoptions(options)
        
        # animation options
        self.time_discretization = options["time_discretization"]
        self.draw_time = options["draw_time"]
        self.dimension = options["dimension"]
        
        # reset time and clear all stored objects
        self.time = [0]
        # remove any object in static & dynamic from server
        self.static_objects: list[ClientVisualObject] = []
        self.dynamic_objects: list[ClientVisualObject] = []
    
    
    def addObjects(self,
                   static: ClientVisualObject | list[ClientVisualObject] = None,
                   dynamic: ClientVisualObject | list[ClientVisualObject] = None):
        '''
        Takes in a visual object or a list of visual objects
        and adds them to the corresponding list
        
        Parameters
        ----------
        static : ClientVisualObject | list[ClientVisualObject]
            static object(s) to add
        dynamic : ClientVisualObject | list[ClientVisualObject]
            dynamic object(s) to add
        '''
        # handle single items
        if static is not None:
            static: list[ClientVisualObject] = toSequence(static)
            self.static_objects.extend(static)
            for obj in static:
                self.client.add_mesh_data(obj.plot_data)
        
        if dynamic is not None:
            dynamic: list[ClientVisualObject] = toSequence(dynamic)
            self.dynamic_objects.extend(dynamic)
            for obj in static:
                self.client.add_mesh_data(obj.plot_data)
        
        self.client.send_mesh_data_list()
    
    
    def remove(self, *objects: ClientVisualObject):
        '''
        Takes in a visual object or a list of visual objects
        and removes them from static and dynamic objects list
        
        Parameters
        ----------
        *objects : ClientVisualObject
            objects to remove from the system
        '''
        for obj in objects:
            if obj in self.static_objects:
                self.static_objects.remove(obj.plot_data)
            elif obj in self.dynamic_objects:
                self.dynamic_objects.remove(obj.plot_data)
        
        # remove mesh data from server
        self.client.clear_mesh_data_list()
        for obj in self.static_objects + self.dynamic_objects:
            self.client.add_mesh_data(obj.plot_data)
    
    
    def updateVisual(self, t_update: float):
        '''
        Appends `t_update` to `time` and updates the dynamic
        objects on the current figure for `t_update` time
        
        Parameters
        ----------
        t_update : float
            duration to update for
        '''
        start_time = self.time[-1] + self.time_discretization
        end_time = self.time[-1] + t_update
        t_vec = np.linspace(start_time, end_time, int(round(t_update/self.time_discretization))).tolist()
        logger.debug("Running Visualization!")
        
        # render if client is connected
        if self.client.ws is None or not self.client.ws.open:
            for t in t_vec:
                # update the dynamic objects on the plotter
                for obj in self.dynamic_objects:
                    move_msgs = toSequence(obj.plot(t))
                    for move_msg in move_msgs:
                        self.client.send_move_object_message(*move_msg)
                time.sleep(self.draw_time)
            
        # append the updated time
        self.time += t_vec
    
    
    def animate(self, t_span: list[float, float] = None,
                time_discretization: float = None,
                pause_time: float = None):
        '''
        Animates from `time` = `t_span[0]` to `t_span[1]`,
        dividing it into frames of length `time_discretization`
        and waiting `pause_time` seconds before rendering the
        next frame. A lower discretization will result in a
        smoother animation, while a `pause_time` lower than
        the discretization will result in a faster animation
        speed. Defaults to 1 second per t
        
        Parameters
        ----------
        t_span : float
            range of time to animate
        time_discretization : float
            time difference between frames
        pause_time : float
            pause time in seconds between frames
        '''
        if t_span is None:
            t_span = (0, self.time[-1])
        if time_discretization is None:
            time_discretization = self.time_discretization
        if pause_time is None:
            pause_time = time_discretization
        
        start_time = t_span[0]
        end_time = t_span[1] + time_discretization
        t_vec = arrange(start_time, end_time, time_discretization)
        
        # animate the dynamic stuff for next `t_update`
        for t in t_vec:
            # get current time
            start_time = datetime.now()

            # update the dynamic objects on the figure
            for obj in self.dynamic_objects:
                move_msgs = toSequence(obj.plot(t))
                for move_msg in move_msgs:
                    self.client.send_move_object_message(*move_msg)
            
            # get current time and subtract from previous time
            # if delta_time > self.draw_time, print lagging message
            draw_time = pause_time - (datetime.now() - start_time).total_seconds()
            if draw_time < 0:
                logger.warning(f"Warning, animation lagging by {-draw_time:.6f}s!")
            
            time.sleep(max(draw_time, 0))
    
    
    @staticmethod
    def get_discretization_and_pause(
        framerate: float = 30, speed: float = 1) -> tuple[float, float]:
        '''
        Returns the time_discretization and pause_time to
        get the desired framerate and speed. Speed of 2
        means 1 second = 2 time
        
        Parameters
        ----------
        framerate : float
            desired framerate
        speed : float
            desired animation speed ratio
        
        Returns
        -------
        time_discretization : float
            time difference between frames
        pause_time : float
            pause time in seconds between frames
        '''
        pause_time = 1 / framerate
        time_discretization = speed / framerate
        return (time_discretization, pause_time)
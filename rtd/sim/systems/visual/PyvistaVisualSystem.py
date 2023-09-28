from rtd.util.mixins import Options
from rtd.sim import SimulationSystem
from rtd.sim.systems.visual import PyvistaVisualObject
from rtd.functional.sequences import toSequence, arrange
from pyvista import Plotter
from datetime import datetime
import numpy as np
import time

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class PyvistaVisualSystem(SimulationSystem, Options):
    '''
    Takes in a list of static and dynamic objects and handles
    their rendering
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "time_discretization": 0.1,
            "draw_time": 0.05,
            "dimension": 3,
        }
    
    
    def __init__(self,
                 static_objects: PyvistaVisualObject | list[PyvistaVisualObject] = None,
                 dynamic_objects: PyvistaVisualObject | list[PyvistaVisualObject] = None,
                 **options):
        # initialize base classes
        SimulationSystem.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.reset()
        self.addObjects(static=static_objects, dynamic=dynamic_objects)
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        
        # animation options
        self.time_discretization = options["time_discretization"]
        self.draw_time = options["draw_time"]
        self.dimension = options["dimension"]
        
        # reset time and clear all stored objects
        self.time = [0]
        self.static_objects: list[PyvistaVisualObject] = []
        self.dynamic_objects: list[PyvistaVisualObject] = []
        
        # Create a new plotter
        self._plotter: Plotter = None
        self.validateOrCreateFigure()
    
    
    def validateOrCreateFigure(self):
        '''
        If plotter does not exists or is no longer valid,
        create a new figure and save its reference to 
        `self._plotter`
        '''
        if self._plotter is None or self._plotter._closed:
            self._plotter = Plotter()
            self._plotter.add_title(f'{self.__class__.__name__}')
            self._plotter.set_background('white')
            self._plotter.add_axes()
    
    
    def addObjects(self,
                   static: PyvistaVisualObject | list[PyvistaVisualObject] = None,
                   dynamic: PyvistaVisualObject | list[PyvistaVisualObject] = None):
        '''
        Takes in a visual object or a list of visual objects
        and adds them to the corresponding list
        '''
        # handle single items
        if static is not None:
            static = toSequence(static)
            self.static_objects.extend(static)
        
        if dynamic is not None:
            dynamic = toSequence(dynamic)
            self.dynamic_objects.extend(dynamic)
    
    
    def remove(self, *objects: PyvistaVisualObject):
        '''
        Takes in a visual object or a list of visual objects
        and removes them from static and dynamic objects list
        '''
        for obj in objects:
            if obj in self.static_objects:
                self.static_objects.remove(obj)
            elif obj in self.dynamic_objects:
                self.dynamic_objects.remove(obj)
    
    
    def updateVisual(self, t_update: float):
        '''
        Appends `t_update` to `time` and updates the dynamic
        objects on the current figure for `t_update` time
        '''
        start_time = self.time[-1] + self.time_discretization
        end_time = self.time[-1] + t_update
        t_vec = np.linspace(start_time, end_time, int(round(t_update/self.time_discretization))).tolist()
        logger.debug("Running Visualization!")
        
        # render if plotter is open
        if self._plotter.iren.initialized and not self._plotter._closed:
            for t in t_vec:
                # update the dynamic objects on the plotter
                for obj in self.dynamic_objects:
                    obj.plot(time=t)
                self._plotter.update()
                time.sleep(self.draw_time)
            
        # append the updated time
        self.time += t_vec
    
    
    def redraw(self, time: float = None, axlim: list = None):
        '''
        Recreates the plotter if necessary and adds the actors
        to the current plotter at the input time. Defaults to
        the most recent `time`
        '''
        if time is None:
            time = self.time[-1]
        
        # if the plotter is closed or invalid, recreate it
        self.validateOrCreateFigure()
        
        # set view based on dimensions
        if self.dimension == 2:
            self._plotter.view_xy(render=False)
        elif self.dimension != 3:
            raise ValueError("Dimension must be 2 or 3!")
        
        # axes bounds
        if axlim is not None:
            if len(axlim) == 4: # auto fit z-axis
                axlim = [*axlim, 0, 0]
            self._plotter.reset_camera(bounds=axlim)
        
        # clear figure content
        self._plotter.clear_actors()
        
        # add objects to the figure
        for obj in self.static_objects + self.dynamic_objects:
            actors = toSequence(obj.create_plot_data(time=time))
            for actor in actors:
                self._plotter.add_actor(actor)
        self._plotter.show(interactive_update=True)
    
    
    def animate(self, t_span: list[float, float] = None,
                time_discretization: float = None,
                pause_time: float = None,
                axlim: list = None):
        '''
        Animates from `time` = `t_span[0]` to `t_span[1]`,
        dividing it into frames of length `time_discretization`
        and waiting `pause_time` seconds before rendering the
        next frame. A lower discretization will result in a
        smoother animation, while a `pause_time` lower than
        the discretization will result in a faster animation
        speed. Defaults to 1 second per t
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
        
        # redraw everything
        self.redraw(0, axlim)
        
        # animate the dynamic stuff for next `t_update`
        for t in t_vec:
            # get current time
            start_time = datetime.now()

            # update the dynamic objects on the figure
            for obj in self.dynamic_objects:
                obj.plot(time=t)
            self._plotter.update()
            
            # get current time and subtract from previous time
            # if delta_time > self.draw_time, print lagging message
            draw_time = pause_time - (datetime.now() - start_time).total_seconds()
            if draw_time < 0:
                logger.warning(f"Warning, animation lagging by {-draw_time:.6f}s!")
            
            time.sleep(max(draw_time, 0))
    
    
    def waituntilclose(self):
        '''
        Waits until plotter is closed before proceeding
        '''
        self._plotter.show()
    
    
    @staticmethod
    def get_discretization_and_pause(
        framerate: float = 30, speed: float = 1) -> tuple[float, float]:
        '''
        Returns the time_discretization and pause_time to
        get the desired framerate and speed. Speed of 2
        means 1 second = 2 time
        '''
        pause_time = 1 / framerate
        time_discretization = speed / framerate
        return (time_discretization, pause_time)
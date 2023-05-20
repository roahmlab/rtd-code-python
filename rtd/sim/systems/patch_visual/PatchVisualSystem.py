from rtd.util.mixins import Options
from rtd.sim import SimulationSystem
from rtd.sim.systems.patch_visual import PatchVisualObject
import matplotlib.pyplot as plt
from datetime import datetime
import time

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class PatchVisualSystem(SimulationSystem, Options):
    '''
    Takes in a list of static and dynamic objects and handles
    their rendering
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            'time_discretization': 0.1,
        }
    
    
    def __init__(self,
                 static_objects: PatchVisualObject | list[PatchVisualObject] = None,
                 dynamic_objects: PatchVisualObject | list[PatchVisualObject] = None,
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
        self.draw_time = 0.05
        
        # reset time and clear all stored objects
        self.time = [0]
        self.static_objects = []
        self.dynamic_objects = []
        
        # Create a new figure
        self.figure_handle = None
        self.validateOrCreateFigure()
    
    
    def validateOrCreateFigure(self):
        '''
        If figure_handle does not exists or is no longer valid,
        create a new figure and save its reference to 
        `self.figure_handle`
        '''
        if (self.figure_handle == None or
        not plt.fignum_exists(self.figure_handle.number)):
            self.figure_handle = plt.figure()
            plt.title(f'Figure 1 - {self.__class__.__name__}')
            # bind pause key
    
    
    def addObjects(self,
                   static: PatchVisualObject | list[PatchVisualObject] = None,
                   dynamic: PatchVisualObject | list[PatchVisualObject] = None):
        '''
        Takes in a visual object or a list of visual objects
        and adds them to the corresponding list
        '''
        if static != None:
            if isinstance(static, list):
                self.static_objects += static
            else:
                self.static_objects.append(static)
        if dynamic != None:
            if isinstance(dynamic, list):
                self.dynamic_objects += dynamic
            else:
                self.dynamic_objects.append(dynamic)
    
    
    def remove(self, *objects):
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
        end_time = self.time[-1] + t_update + self.time_discretization
        count = (end_time - start_time) / self.time_discretization
        t_vec = [start_time + i*self.time_discretization for i in range(int(count))]
        logger.debug("Running Visualization!")
        
        # try to set current figure
        try:
            ax = self.figure_handle.axes[-1]
            self.figure_handle.show()
            
            # animate the next `t_update`
            for t in t_vec:
                # update the dynamic objects on the figure
                for obj in self.dynamic_objects:
                    obj.plot(time=t)
                self.figure_handle.canvas.draw()
                self.figure_handle.canvas.flush_events()
                time.sleep(self.draw_time)
        except Exception as e:
            print(e)
            
        # append the updated time
        self.time += t_vec
    
    
    def redraw(self, time: float = None):
        '''
        Recreates the figure handle if necessary and adds
        the artist objects to the current figure at the
        input time. Defaults to the most recent `time`
        '''
        if time == None:
            time = self.time[-1]
        
        # if the figure is closed or invalid, recreate it
        self.validateOrCreateFigure()
        
        # activate the current figure
        ax = self.figure_handle.axes[-1]
        self.figure_handle.show()
        
        # clear figure content
        for artist in ax.patches + ax.collections:
            artist.remove()
        
        # add objects to the figure
        for obj in self.static_objects:
            artist = obj.plot(time=time)
            ax.add_artist(artist)
        for obj in self.dynamic_objects:
            artist = obj.plot(time=time)
            ax.add_artist(artist)
        self.figure_handle.canvas.draw()
        self.figure_handle.canvas.flush_events()
    
    
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
        '''
        if t_span == None:
            t_span = (0, self.time[-1])
        if time_discretization == None:
            time_discretization = self.time_discretization
        if pause_time == None:
            pause_time = time_discretization
        
        start_time = t_span[0]
        end_time = t_span[1] + time_discretization
        count = (end_time - start_time) / time_discretization
        t_vec = [start_time + i*time_discretization for i in range(int(count))]
        
        # redraw everything
        self.redraw(0)
        
        # animate dynamic objects
        ax = self.figure_handle.axes[-1]
        self.figure_handle.show()
        
        # animate the next `t_update`
        for t in t_vec:
            # get current time
            start_time = datetime.now()

            # update the dynamic objects on the figure
            for obj in self.dynamic_objects:
                obj.plot(time=t)
            self.figure_handle.canvas.draw()
            self.figure_handle.canvas.flush_events()
            
            # compute wait time
            draw_time = pause_time - (datetime.now() - start_time).total_seconds()
            if draw_time < 0:
                logger.warning(f"Warning, animation lagging by {-draw_time:.6f}s!")
            
            time.sleep(max(draw_time, 0))
            # get current time and subtract from previous time
            # if delta_time > self.draw_time, print lagging message
        
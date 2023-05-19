from rtd.util.mixins import Options
from rtd.sim import SimulationSystem
from rtd.sim.systems.patch_visual import PatchVisualObject
import matplotlib.pyplot as plt
import numpy as np
import time



class PatchVisualSystem(SimulationSystem, Options):
    '''
    Takes in a list of static and dynamic objects and handles
    their rendering
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            'time_discretization': 0.1,
            'log_collisions': False,
            'enable_camlight': False,
        }
    
    
    def __init__(self, static_objects = None, dynamic_objects = None, **options):
        # initialize base classes
        SimulationSystem.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.reset()
        self.addObjects(static=static_objects, dynamic=dynamic_objects)
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        
        self.time_discretization = options["time_discretization"]
        self.draw_time = 0.05
        
        # reset time and clear all stored objects
        self.time = [0]
        self.static_objects = list()
        self.dynamic_objects = list()
        
        # set camlight flag
        self.enable_camlight = options["enable_camlight"]
        
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
            # graphic smoothing off
    
    
    def addObjects(self, static=None, dynamic=None):
        '''
        Takes in a visual object or a list of visual objects
        and adds them to the corresponding list
        '''
        if static != None:
            self.static_objects.append(static)
        if dynamic != None:
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
    
    
    def updateVisual(self, t_update):
        '''
        Updates `time` to include the next `t_update` time
        and animates the next `t_update` time
        '''
        start_time = self.time[-1] + self.time_discretization
        end_time = self.time[-1] + t_update + self.time_discretization
        count = (end_time - start_time) / self.time_discretization
        t_vec = [start_time + i*self.time_discretization for i in range(int(count))]
        # LOG DEBUG "Running visualization!"
        
        # try to set current figure
        try:
            plt.figure(self.figure_handle.number)
            ax = self.figure_handle.axes[-1]
            self.figure_handle.show()
            
            # plot each of the time requested
            for t_plot in t_vec:
                # get current time
                for obj in self.dynamic_objects:
                    artist = obj.get_plot_data(time=t_plot)
                    #print(f"{artist=}")
                    ax.add_artist(artist)
                self.figure_handle.canvas.draw()
                self.figure_handle.canvas.flush_events()
                #time.sleep(self.draw_time)
                # get current time and subtract from previous time
                # if delta_time > self.draw_time, print lagging message
        except Exception as e:
            print(e)
            
        # save the time change
        self.time.append(t_vec)
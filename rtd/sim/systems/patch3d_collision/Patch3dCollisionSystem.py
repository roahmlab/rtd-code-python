from rtd.util.mixins import Options
from rtd.sim import SimulationSystem
from rtd.sim.systems.patch3d_collision import Patch3dObject, Patch3dDynamicObject
from rtd.functional.sequences import toSequence, arrange_list
from trimesh.collision import CollisionManager

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class Patch3dCollisionSystem(SimulationSystem, Options):
    '''
    Takes in a list of Patch3dObject and Patch3dDynamicObjects
    and handles their collision detection
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "time_discretization": 0.1,
        }
    
    
    def __init__(self,
                 static_objects: Patch3dObject | list[Patch3dObject] = None,
                 dynamic_objects: Patch3dDynamicObject | list[Patch3dDynamicObject] = None,
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
        
        # collision options
        self.time_discretization = options["time_discretization"]
        self._collision_handle = CollisionManager()
        
        # reset time and clear all stored objects
        self.time = [0]
        self.static_objects = []
        self.dynamic_objects = []
    
    
    def addObjects(self,
                   static: Patch3dObject | list[Patch3dObject] = None,
                   dynamic: Patch3dDynamicObject | list[Patch3dDynamicObject] = None):
        '''
        Takes in a collision object or a list of collision objects
        and adds them to the corresponding list
        '''
        # handle single items
        static = toSequence(static)
        dynamic = toSequence(dynamic)
        
        self.static_objects.extend(static)
        self.dynamic_objects.extend(dynamic)
        
        # add the static objects to the collision handle
        for obj in static:
            self._collision_handle.add_object(str(id(obj)), obj.mesh)
    
    
    def remove(self, *objects):
        '''
        Takes in a collision object or a list of collision objects
        and removes them from static and dynamic objects list
        '''
        for obj in objects:
            if obj in self.static_objects:
                self.static_objects.remove(obj)
            elif obj in self.dynamic_objects:
                self.dynamic_objects.remove(obj)
    
    
    def updateCollision(self, t_update: float):
        '''
        Appends `t_update` to `time` and checks for any collision
        for `t_update` time
        '''
        start_time = self.time[-1] + self.time_discretization
        end_time = self.time[-1] + t_update + self.time_discretization
        t_vec = arrange_list(start_time, end_time, self.time_discretization)
        logger.debug("Running collision check!")
        
        # accumulate the return
            
        # append the updated time
        self.time += t_vec
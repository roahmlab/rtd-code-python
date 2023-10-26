from rtd.util.mixins import Options
from rtd.sim import SimulationSystem
from rtd.sim.systems.collision import CollisionObject, DynamicCollisionObject
from rtd.functional.sequences import toSequence
import numpy as np

# define top level module logger
import logging
logger = logging.getLogger(__name__)

# type hinting
CollisionPair = tuple[int, int]



class TrimeshCollisionSystem(SimulationSystem, Options):
    '''
    Takes in a list of CollisionObjects and DynamicCollisionObjects
    and handles their collision detection
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "time_discretization": 0.1,
        }
    
    
    def __init__(self,
                 static_objects: CollisionObject | list[CollisionObject] = None,
                 dynamic_objects: DynamicCollisionObject | list[DynamicCollisionObject] = None,
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
        
        # reset time and clear all stored objects
        self.time = [0]
        self.static_objects: list[CollisionObject] = list()
        self.dynamic_objects: list[DynamicCollisionObject] = list()
    
    
    def addObjects(self,
                   static: CollisionObject | list[CollisionObject] = None,
                   dynamic: DynamicCollisionObject | list[DynamicCollisionObject] = None):
        '''
        Takes in a collision object or a list of collision objects
        and adds them to the corresponding list
        
        Parameters
        ----------
        static : CollisionObject | list[CollisionObject]
            static object(s) to add
        dynamic : DynamicCollisionObject | list[DynamicCollisionObject]
            dynamic object(s) to add
        '''
        # handle single items
        if static is not None:
            static: list[CollisionObject] = toSequence(static)
            self.static_objects.extend(static)
                
        if dynamic is not None:
            dynamic = toSequence(dynamic)
            self.dynamic_objects.extend(dynamic)
    
    
    def remove(self, *objects: CollisionObject | DynamicCollisionObject):
        '''
        Takes in a collision object or a list of collision objects
        and removes them from static and dynamic objects list. 
        Assumes the object is already in either lists
        
        Parameters
        ----------
        *objects : CollisionObject | DynamicCollisionObject
            objects to remove from the system
        '''
        for obj in objects:
            if obj in self.static_objects:
                self.static_objects.remove(obj)
            elif obj in self.dynamic_objects:
                self.dynamic_objects.remove(obj)
    
    
    def updateCollision(self, t_update: float) -> tuple[bool, set[CollisionPair]]:
        '''
        Appends `t_update` to `time` and checks for any collision
        for `t_update` time
        
        Parameters
        ----------
        t_update : float
            duration to update for
        
        Returns
        -------
        collided: bool
            whether a collision occured
        pairs : set[tuple[int, int]]
            set of collided objects pairs
        '''
        start_time = self.time[-1] + self.time_discretization
        end_time = self.time[-1] + t_update
        t_vec = np.linspace(start_time, end_time, int(round(t_update/self.time_discretization))).tolist()
        logger.debug("Running collision check!")
        
        # accumulate collision result over time
        collided = False
        pairs = set()
        for t in t_vec:
            res = self.checkCollisionAtTime(time=t)
            collided |= res["collided"]
            pairs.update(res["pairs"])
            
        # append the updated time
        self.time += t_vec
        
        # log contact pairs
        if collided:
            logger.debug(f"Contact pairs: {pairs}")
        
        return (collided, pairs)
    
    
    def checkCollisionAtTime(self, time: float) -> dict:
        '''
        Check for every collision at a given time and return
        a bool if any collision happened, as well as a set of
        collided pair's parents and the number of pairs
        
        Parameters
        ----------
        time : float
            time to check collision at
        
        Returns
        -------
        info : dict
            with keys:
        <time> : float
            input time
        <collided> : bool
            whether a collision occured
        <n_pairs> : int
            number of collided pairs
        <pairs> : set[tuple[int, int]]
            set of collided object pairs
        '''
        collided: bool = False
        pairs: set[CollisionPair] = set()
        
        resolved = [obj.getCollisionObject(time=time) for obj in self.dynamic_objects]
        
        for dyn1_i in range(len(resolved)):
            dyn1 = resolved[dyn1_i]
            
            # check each dynamic object with each static object
            for stat in self.static_objects:
                if dyn1.parent != stat.parent:
                    c, pair = dyn1.inCollision(stat)
                    if c: pairs.add(pair)
                    collided |= c
            
            # check each dynamic object with remaining dynamic objects
            for dyn2_i in range(dyn1_i+1, len(resolved)):
                dyn2 = resolved[dyn2_i]
                if dyn1.parent != dyn2.parent:
                    c, pair = dyn1.inCollision(dyn2)
                    if c: pairs.add(pair)
                    collided |= c
        
        # logging
        if collided:
            logger.error(f"Collision at t={time:.2f} detected!")
            logger.debug("Collision pairs are as follows")
            for obj1, obj2 in pairs:
                logger.debug(f"Collision detected between {obj1} and {obj2}")
        
        return {
            "time": time,
            "collided": collided,
            "n_pairs": len(pairs),
            "pairs": pairs,
        }

    
    def checkCollisionObject(self, collision_obj: CollisionObject) -> dict:
        '''
        Check for every collision against collision_obj (does not
        check for internal collision) at the most recent time
        
        Parameters
        ----------
        collision_obj : CollisionObject
            object to check collision against
        
        Returns
        -------
        info : dict
            with keys:
        <time> : float
            input time
        <collided> : bool
            whether a collision occured
        <n_pairs> : int
            number of collided pairs
        <pairs> : set[tuple[int, int]]
            set of collided object pairs
        '''
        time = self.time[-1]
        resolved = (obj.getCollisionObject(time=time) for obj in self.dynamic_objects)
        
        # accumulate collision result over time
        collided = False
        pairs: set[CollisionPair] = set()
        
        # check against static objects
        for obj in self.static_objects:
            col, pair = obj.inCollision(collision_obj)
            collided |= col
            if col:
                pairs.add(pair)
        # check against dynamic objects
        for obj in resolved:
            col, pair = obj.inCollision(collision_obj)
            collided |= col
            if col:
                pairs.add(pair)
        
        return {
            "time": time,
            "collided": collided,
            "n_pairs": len(pairs),
            "pairs": pairs,
        }
from rtd.util.mixins import Options
from rtd.sim import SimulationSystem
from rtd.sim.systems.patch3d_collision import Patch3dObject, Patch3dDynamicObject
from rtd.functional.sequences import toSequence, arrange_list
from trimesh.collision import CollisionManager

# define top level module logger
import logging
logger = logging.getLogger(__name__)

# type hinting
CollisionPair = tuple[Patch3dObject, Patch3dObject]
CollisionIDPair = tuple[int, int]



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
        
        # reset time and clear all stored objects
        self.time = [0]
        self.static_objects = []
        self.dynamic_objects = []
        
        # collision handle, returns a set of
        # the collided pair's ids
        self._collision_handle = CollisionManager()
        # store id(object): object.parent to
        # make sense of the collision handle output
        self._name_refs = dict()
    
    
    def addObjects(self,
                   static: Patch3dObject | list[Patch3dObject] = None,
                   dynamic: Patch3dDynamicObject | list[Patch3dDynamicObject] = None):
        '''
        Takes in a collision object or a list of collision objects
        and adds them to the corresponding list
        '''
        # handle single items
        if static != None:
            static = toSequence(static)
            self.static_objects.extend(static)
            
            # add the static objects to the collision handle
            # using its id as the name, and reference the id
            # to the object's parent
            for obj in static:
                self._collision_handle.add_object(name=id(obj), mesh=obj.mesh)
                self._name_refs[id(obj)] = obj.parent
                
        if dynamic != None:
            dynamic = toSequence(dynamic)
            self.dynamic_objects.extend(dynamic)
    
    
    def remove(self, *objects):
        '''
        Takes in a collision object or a list of collision objects
        and removes them from static and dynamic objects list. 
        Assumes the object is already in either lists
        '''
        for obj in objects:
            if obj in self.static_objects:
                self.static_objects.remove(obj)
                self._collision_handle.remove_object(id(obj))
                self._name_refs.pop(id(obj))
            elif obj in self.dynamic_objects:
                self.dynamic_objects.remove(obj)
                # no need to remove from collision handle
                # and name references as they only exist
                # during the collision check
    
    
    def updateCollision(self, t_update: float) -> tuple[bool, set[CollisionPair]]:
        '''
        Appends `t_update` to `time` and checks for any collision
        for `t_update` time
        '''
        start_time = self.time[-1] + self.time_discretization
        end_time = self.time[-1] + t_update + self.time_discretization
        t_vec = arrange_list(start_time, end_time, self.time_discretization)
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
        '''
        # resolve dynamic object and add to handle
        for obj in self.dynamic_objects:
            resolved = obj.getCollisionObject(time=time)
            self._collision_handle.add_object(name=id(obj), mesh=resolved.mesh)
            self._name_refs[id(obj)] = resolved.parent
        
        # check collision
        collided, names = self._collision_handle.in_collision_internal(return_names=True)
        
        # get pairs of collided pair's parents
        pairs = self._dereference_pairs(names) if collided else set()
        
        # logging
        if collided:
            logger.error(f"Collision at t={time:.2f} detected!")
            logger.debug("Collision pairs are as follows")
            for obj1, obj2 in pairs:
                logger.debug(f"Collision detected between {obj1} and {obj2}")
        
        # remove dynamic objects from handle and reference
        for obj in self.dynamic_objects:
            self._collision_handle.remove_object(id(obj))
            self._name_refs.pop(id(obj))
        
        return {
            "time": time,
            "collided": collided,
            "n_pairs": len(pairs),
            "pairs": pairs,
        }
    
    
    def _dereference_pairs(self, names: set[CollisionIDPair]) -> set[CollisionPair]:
        '''
        Takes in a set of pairs of collided object ids and
        dereferences it to create a set of pairs of the collided
        pair's parents, ignoring pairs with the same parent
        '''
        pairs = set()
        for name1, name2 in names:
            # get parents
            obj1 = self._name_refs[name1]
            obj2 = self._name_refs[name2]
            
            # ignore if they share the same parent
            if obj1 == obj2 and obj1 != None:
                pass
            
            pairs.add((obj1, obj2))
            
        return pairs

    
    def checkCollisionObject(self, collision_obj: Patch3dObject) -> dict:
        '''
        Check for every collision against collision_obj (does not
        check for internal collision) at the most recent time
        '''
        time = self.time[-1]
        resolved = (obj.getCollisionObject(time=time) for obj in self.dynamic_objects)
        
        # accumulate collision result over time
        collided = False
        pairs = set()
        
        # check against static objects
        for obj in self.static_objects:
            res, pair = obj.inCollision(collision_obj)
            collided |= res
            if res:
                pairs.add(pair)
        # check against dynamic objects
        for obj in resolved:
            res, pair = obj.inCollision(collision_obj)
            collided |= res
            if res:
                pairs.add(pair)
        
        return {
            "time": time,
            "collided": collided,
            "n_pairs": len(pairs),
            "pairs": pairs,
        }
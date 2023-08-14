from rtd.util.mixins import Options
from rtd.sim import SimulationSystem
from rtd.sim.systems.collision import CollisionObject, DynamicCollisionObject
from rtd.functional.sequences import toSequence, arrange_list
from trimesh.collision import CollisionManager

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
        
        # collision handle, returns a set of
        # the collided pair's ids
        self._collision_handle = CollisionManager()
        # store id(object): object.parent to
        # make sense of the collision handle output
        self._name_refs: dict[int, int] = dict()
    
    
    def addObjects(self,
                   static: CollisionObject | list[CollisionObject] = None,
                   dynamic: DynamicCollisionObject | list[DynamicCollisionObject] = None):
        '''
        Takes in a collision object or a list of collision objects
        and adds them to the corresponding list
        '''
        # handle single items
        if static is not None:
            static: list[CollisionObject] = toSequence(static)
            self.static_objects.extend(static)
            
            # add each mesh of each static objects to the collision
            # handle using the mesh id as the name, and reference the
            # id to the static object's parent
            for obj in static:
                for mesh in obj.meshes:
                    self._collision_handle.add_object(name=id(mesh), mesh=mesh)
                    self._name_refs[id(mesh)] = obj.parent
                
        if dynamic is not None:
            dynamic = toSequence(dynamic)
            self.dynamic_objects.extend(dynamic)
    
    
    def remove(self, *objects: CollisionObject | DynamicCollisionObject):
        '''
        Takes in a collision object or a list of collision objects
        and removes them from static and dynamic objects list. 
        Assumes the object is already in either lists
        '''
        for obj in objects:
            if obj in self.static_objects:
                self.static_objects.remove(obj)
                for mesh in obj.meshes:
                    self._collision_handle.remove_object(id(mesh))
                    self._name_refs.pop(id(mesh))
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
        added_meshes_ids = list()
        for obj in self.dynamic_objects:
            resolved = obj.getCollisionObject(time=time)
            for mesh in resolved.meshes:
                self._collision_handle.add_object(name=id(mesh), mesh=mesh)
                self._name_refs[id(mesh)] = resolved.parent
                added_meshes_ids.append(id(mesh))
        
        # check collision
        collided, names = self._collision_handle.in_collision_internal(return_names=True)
        
        # get pairs of collided pair's parents
        pairs: set[CollisionPair] = self._dereference_pairs(names) if collided else set()
        
        # logging
        if collided:
            logger.error(f"Collision at t={time:.2f} detected!")
            logger.debug("Collision pairs are as follows")
            for obj1, obj2 in pairs:
                logger.debug(f"Collision detected between {obj1} and {obj2}")
        
        # remove dynamic objects from handle and reference
        for mesh_id in added_meshes_ids:
            self._collision_handle.remove_object(mesh_id)
            self._name_refs.pop(mesh_id)
        
        return {
            "time": time,
            "collided": collided,
            "n_pairs": len(pairs),
            "pairs": pairs,
        }
    
    
    def _dereference_pairs(self, names: set[CollisionPair]) -> set[CollisionPair]:
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
            if obj1 == obj2 and obj1 is not None:
                pass
            
            pairs.add((obj1, obj2))
            
        return pairs

    
    def checkCollisionObject(self, collision_obj: CollisionObject) -> dict:
        '''
        Check for every collision against collision_obj (does not
        check for internal collision) at the most recent time
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
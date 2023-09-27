from abc import ABCMeta, abstractmethod
from rtd.planner.reachsets import ReachSetInstance
from rtd.entity.states import EntityState



class ReachSetGenerator(metaclass=ABCMeta):
    '''
    Base class for the generation of reacheable sets for the planner
    
    The ReachSetGenerator class interfaces out the generation of reachable
    sets for the RTD planner. It contains a built-in cache which is enabled
    if `cache_max_size > 0`. Caching is based on the id of the robot's state
    and any extra arguments passed through the `getReachableSet` method. This
    class can be used to encapsulate reachable sets generated offline, or the
    online computation of reachable sets. It acts as a generator for a single
    instance of ReachableSet
    '''
    def __init__(self):
        self.cache_max_size: float = None
        # a list of length < cache_max_size that stores
        # (hash, reachableset) pairs
        self._cache: list[tuple[str, dict[int, ReachSetInstance]]] = list()
    
    
    @abstractmethod
    def generateReachableSet(self, robotState: EntityState, **options) -> dict[int, ReachSetInstance]:
        '''
        Generate a new reachable set given a robot state and extra arguments if desired
        
        This method generates the relevant reachable set for the
        `robotState` provided and outputs the singular instance of some
        reachable set. It should always create a new instance of a
        ReachableSetInstance
        
        Arguments:
            robotState: EntityState: Some entity state which the ReachableSetInstance is generated for.
        
        Returns:
            dict: A dict of problem id to `ReachSetInstance` pairs
        '''
        pass
    
    
    def getReachableSet(self, robotState: EntityState,
                        ignore_cache: bool = False, **options) -> dict[int, ReachSetInstance]:
        '''
        Get a reachable set instance for the given robot state and passthrough arguments
        
        This function handles how to actually get the reachable set
        with built in caching of already generated instances. It will
        call `generateReachableSet` as needed. This is useful if we
        need to use one reachable set in another reachable set and we
        don't want to regenerate it online. It performs caching based
        on the id of the provided robotState and and the string cast
        of any additional arguments. If we don't want to use the cache
        on one call, setting `ignore_cache` to true will bypass caching
        altogether
        
        Arguments:
            robotState: EntityState: Some state of used for generation / keying
            ignore_cache: bool: If set true, the cache is completely ignored
        
        Returns:
            dict: A dict of problem id to `ReachSetInstance` pairs
        '''
        # if we don't want to use the cache or don't have a cache,
        # return a newly generated reachableset
        if ignore_cache or self.cache_max_size < 1:
            return self.generateReachableSet(robotState, **options)
        
        # create hash of the input argument based on the robotState id
        # and string representation of the keyword arguments
        cache_hash = str(id(robotState)) + str(options)
        
        # search cache if hash exists and return if it does
        for rs in self._cache:
            if rs[0] == cache_hash:
                return rs[1]
        
        # otherwise generate a reachableset and add it to the cache
        reachableset = self.generateReachableSet(robotState, **options)
        self._cache.append((cache_hash, reachableset))
        if len(self._cache) > self.cache_max_size:
            self._cache.pop(0)
        return reachableset
from rtd.sim.world import WorldEntity
from rtd.entity.components import GenericEntityState
from rtd.entity.box_obstacle import BoxObstacleInfo, BoxObstacleVisual, BoxObstacleCollision



class BoxObstacle(WorldEntity):
    '''
    A 3D box obstacle with an info, state, visual, and collision component
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "components": {
                "info": BoxObstacleInfo,
                "state": GenericEntityState,
                "visual": BoxObstacleVisual,
                "collision": BoxObstacleCollision,
            },
        }
    
    
    def __init__(self, info: BoxObstacleInfo = BoxObstacleInfo,
                 state: GenericEntityState = GenericEntityState,
                 visual: BoxObstacleVisual = BoxObstacleVisual,
                 collision: BoxObstacleCollision = BoxObstacleCollision, **options):
        '''
        Creates a BoxObstacle, taking in an info, state, and visual components.
        The components can either be a class or an instance of a class. If
        given a class, it will create the default component of that class.
        If given an instance, it will copy the type and options of that
        instance and reconstruct that component
        '''
        WorldEntity.__init__(self)
        components = {
            "info": info,
            "state": state,
            "visual": visual,
            "collision": collision,
        }
        # Get override options based on provided components
        override_options = self.get_componentOverrideOptions(components)
        
        # Merge all options
        self.mergeoptions(options, override_options)
        
        # (Re)construct all components for consistency
        self.construct_components("info")
        self.construct_components("state", self.info)
        self.construct_components("visual", self.info, self.state)
        self.construct_components("collision", self.info, self.state)
        
        # reset
        self.reset()
    
    
    def reset(self, **options):
        self.mergeoptions(options)
        self.reset_components()
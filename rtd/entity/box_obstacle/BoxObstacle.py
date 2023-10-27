from rtd.sim.world import WorldEntity
from rtd.entity.components import GenericEntityState
from rtd.entity.box_obstacle import BoxObstacleInfo, BoxObstacleVisual, BoxObstacleCollision, BoxObstacleZonotope



class BoxObstacle(WorldEntity):
    '''
    A 3D box obstacle with an info, state, visual, and collision component
    '''
    @staticmethod
    def defaultoptions() -> dict:
        """
        Returns
        -------
        options : dict
            default options of BoxObstacle
        """
        return {
            "components": {
                "info": BoxObstacleInfo,
                "state": GenericEntityState,
                "visual": BoxObstacleVisual,
                "collision": BoxObstacleCollision,
                "representation": BoxObstacleZonotope,
            },
        }
    
    
    def __init__(self, info: BoxObstacleInfo = BoxObstacleInfo,
                 state: GenericEntityState = GenericEntityState,
                 visual: BoxObstacleVisual = BoxObstacleVisual,
                 collision: BoxObstacleCollision = BoxObstacleCollision, 
                 representation: BoxObstacleZonotope = BoxObstacleZonotope, **options):
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
            "representation": representation,
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
        self.construct_components("representation", self.info, self.state)
        
        # reset
        self.reset()
    
    
    def reset(self, **options):
        self.mergeoptions(options)
        self.reset_components()


    @staticmethod
    def make_box(center: tuple[float] = (0,0,0), dims: tuple[float] = (0, 0, 0),
                 color: tuple[float] = (1, 0, 1)) -> 'BoxObstacle':
        '''
        Creates a box obstacle with the specified parameters
        
        Parameters
        ----------
        center : tuple[float]
            x, y, z coordinate of the box center
        dims : tuple[float]
            x, y, z dimensions of the box obstacle
        color : tuple[float]
            r, g, b color of box
        
        Returns
        -------
        box : BoxObstacle
            BoxObtacle instance with specified parameters
        '''
        info = BoxObstacleInfo(dims=dims, color=color)
        state = GenericEntityState(info, initial_state=center)
        state.reset()
        visual = BoxObstacleVisual(info, state)
        collision = BoxObstacleCollision(info, state)
        return BoxObstacle(info, state, visual, collision)
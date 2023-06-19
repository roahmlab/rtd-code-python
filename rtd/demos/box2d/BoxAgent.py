from rtd.sim.world import WorldEntity
from rtd.entity.components import GenericEntityState
from rtd.demos.box2d import BoxAgentInfo, BoxAgentVisual



class BoxAgent(WorldEntity):
    '''
    A 2D box agent with an info, state, and visual component. 
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "components": {
                "info": BoxAgentInfo,
                "state": GenericEntityState,
                "visual": BoxAgentVisual,
            },
        }
    
    
    def __init__(self, info: BoxAgentInfo = BoxAgentInfo,
                 state: GenericEntityState = GenericEntityState,
                 visual: BoxAgentVisual = BoxAgentVisual, **options):
        '''
        Creates a BoxAgent, taking in an info, state, and visual components.
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
        }
        # Get override options based on provided components
        override_options = self.get_componentOverrideOptions(components)
        
        # Merge all options
        self.mergeoptions(options, override_options)
        
        # (Re)construct all components for consistency
        self.construct_components("info")
        self.construct_components("state", self.info)
        self.construct_components("visual", self.info, self.state)
        
        # reset
        self.reset()
    
    
    def reset(self, **options):
        self.mergeoptions(options)
        self.reset_components()
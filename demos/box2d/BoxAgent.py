from rtd.sim.world import WorldEntity
from rtd.entity.components import EmptyInfoComponent, GenericEntityState
from demos.box2d import BoxAgentInfo



class BoxAgent(WorldEntity):
    '''
    A 2D box agent with an info, state, and
    visual component. 
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "components": {
                "info": BoxAgentInfo,
                "state": GenericEntityState,
            },
        }
    
    
    def __init__(self, components: dict = None, **options):
        '''
        Creates a BoxAgent, taking in a dict with the
        `component_name` and object. It will copy the type
        and the options of the object, saving it under 
        `options["components"][component_name]` and
        `options["component_options"][component_name]`,
        and saving the component under `self.component_name`.
        
        If no `components` is provided, it will create a
        default `info` and `state` property of type as defined
        under `defaultoptions()`. If some components are
        omitted, e.g., the state, it will use the remaining
        provided components and use the default options for that
        component otherwise
        '''
        WorldEntity.__init__(self)
        # Get override options based on provided components
        if components != None:
            override_options = self.get_componentOverrideOptions(components)
        else:
            override_options = dict()
        
        # Merge all options
        self.mergeoptions(options, override_options)
        
        # (Re)construct all components for consistency
        self.construct_components("info")
        self.construct_components("state", self.info)
        
        # reset
        self.reset()
    
    
    def reset(self, **options):
        self.mergeoptions(options)
        self.reset_components()
from rtd.util.mixins import Options



class WorldEntity(Options):
    '''
    A base class for entities. Allows for the management of components.
    Abstract methods such as `defaultoptions` must still be implemented.
    Requires `options` to be set up in a specific way to function (more
    details in the function comments below)
    '''
    def construct_components(self, component_name: str, *component_args):
        '''
        Creates component of type `options["components"][component_name]`, taking
        in `component_args` and `options["component_options"][component_name]`
        as an argument, saving it under `self.component_name`
        
        E.g.,
        options["components"]["state"] = GenericEntityState
        options["component_options]["state"] = {"n_states": 5}
        
        construct_components("state", EmptyInfoComponent()) will run
        self.state = GenericEntityState(EmptyInfoComponent(), n_states=5)
        '''
        options = self.getoptions()
        
        # create component with provided args
        component = options["components"][component_name](*component_args)
        
        # if component option is defined for that component, use it
        if "component_options" in options and component_name in options["component_options"]:
            component = options["components"][component_name](
                *component_args,
                **options["component_options"][component_name]
            )
        else:
            component = options["components"][component_name](*component_args)
        
        # save under self.component_name
        setattr(self, component_name, component)
    
    
    def reset_components(self):
        '''
        Resets every component
        
        E.g.,
        options["components"] = {"info": EmptyInfoComponent,
                                "state": GenericEntityState},
        options["component_options"] = {"state": {"n_states": 5}}
        
        reset_components() will run
        self.info.reset()
        self.state.reset(n_states=5)
        '''
        options = self.getoptions()
        
        for component_name in options["components"]:
            # if component option is defined for that component, reset using that
            if "component_options" in options and component_name in options["component_options"]:
                getattr(self, component_name).reset(**options["component_options"][component_name])
            else:
                getattr(self, component_name).reset()
    
    
    @staticmethod
    def get_componentOverrideOptions(components: dict) -> dict:
        '''
        Takes in a dict of components and saves their type under
        `options["components"][component_name] and options under
        `options["component_options"][component_name]`. Useful, for
        example, inside the entity constructor to input pre-generated
        components so that `construct_components` and `reset_components`
        keep the options of the original input components
        '''
        options = {"components": dict(), "component_options": dict()}
        
        for component_name, component in components.items():
            # set `options["components"]` to type of component so
            # the component can be constructed inside
            # `construct_components`
            options["components"][component_name] = type(component)
            
            # if the component inherits Options, copy all of its
            # options and store them under `options["component_options"]`
            if issubclass(type(component), Options):
                options["component_options"][component_name] = component.getoptions()
        
        return options
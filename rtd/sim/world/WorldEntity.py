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
        Takes in a `component_name` and constructs that component as
        `self.component_name` of type `options["components"]`, using
        `component_args` and `options["component_options"]` defined
        for that `component_name`
        
        E.g.,
        options["components"]["state"] = GenericEntityState
        options["component_options]["state"] = {"n_states": 5}
        
        construct_components("state", EmptyInfoComponent()) will run:
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
                                "state": GenericEntityState}
        options["component_options"] = {"state": {"n_states": 5}}
        
        reset_components() will run:
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
        Takes in a dict of components classes or instances. It saves
        the component type under `options["components"]` and saves
        their options, if provided, under `options["component_options"]
        
        E.g.,
        components = {"info": EmptyInfoState,                   # class
                     "state": GenericEntityState(n_states=5)}   # instance
        
        get_componentOverrideOptions(components) will result in
        options["components"] = {"info": EmptyInfoState,
                                "state": GenericEntityState}
        options["component_options"] = {"state": {"n_states": 5}}
        
        '''
        options = {"components": dict(), "component_options": dict()}
        
        for component_name, component in components.items():
            # save component type under `options["components"]`
            if isinstance(component, type):
                options["components"][component_name] = component
            else:
                options["components"][component_name] = type(component)
            
            # if the component inherits Options, copy all of its
            # options and store them under `options["component_options"]`
            if (component_options := WorldEntity.get_componentOptions(component)) != None:
                options["component_options"][component_name] = component_options
        
        return options
    
    
    @staticmethod
    def get_componentOptions(component) -> dict:
        '''
        Takes in a component class or instance and returns either
        the defaultoptions of that class or the actual options of
        that instance if the component inherits from options.
        Otherwise returns None
        '''
        # if the input is a component class that inherits Options
        if isinstance(component, type):
            if issubclass(component, Options): 
                return component.defaultoptions()
        
        # if the input is a component instance that inherits Options
        elif issubclass(type(component), Options):
            return component.getoptions()
        
        # component does not inherit Options
        return None
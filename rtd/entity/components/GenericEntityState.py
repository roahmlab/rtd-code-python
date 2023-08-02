from rtd.entity.components import BaseInfoComponent, BaseStateComponent
from rtd.util.mixins import Options
from rtd.functional.interpolate import interp1_list
from random import uniform



class GenericEntityState(BaseStateComponent, Options):
    '''
    A generic entity state that stores an (n_states, :) list to keep track
    of the state at each point in time. New states can be appended by calling
    `commit_state_data` with the time interval and new state. A state at any
    moment can be retrieved by calling `get_state`. It will default to the most
    recent state
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return dict()
    
    
    def __init__(self, entity_info: BaseInfoComponent, **options):
        # initialize base classes
        BaseStateComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.entityinfo = entity_info
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        
        # Select the number of states either from the dimension of the
        # entity, or from the option passed in
        if "n_states" in options:
            self.n_states = options["n_states"]
        else:
            self.n_states = self.entityinfo.dimension
            
        # Either start with zeros or use the provided initial state if given
        if "initial_state" in options:
            if len(options["initial_state"]) != self.n_states:
                raise ValueError("Dimension of initial state and number of states must match!")
            self.state = [options["initial_state"]]
        else:
            self.state = [[0] * self.n_states]
        
        # start at time 0
        self.time = [0]
    
    
    def random_init(self, state_range: tuple[float, float],
                    save_to_options: bool = False):
        '''
        Randomly initializes the first state from the given range
        `start_range[0]:start_range[1]` (inclusive). Will save
        the initial state to options so that it will revert to this
        state when `reset` is called
        '''
        self.state = [[uniform(*state_range) for _ in range(self.n_states)]]
        self.time = [0]
        
        if save_to_options:
            self.mergeoptions({"initial_state": self.state[0]})
        
    
    def get_state(self, time: float = None) -> dict:
        '''
        Gets the state at a specific time (defaults to most recent
        time), interpolating the values if needed
        '''
        # default to last time
        if time is None:
            time = self.time[-1]
            
        # get state at time, interporate if needed
        state = interp1_list(self.time, self.state, time)
        
        return {
            "time": time,
            "state": state,
        }
    
    
    def commit_state_data(self, time: float, state: list[float]):
        '''
        Takes in a state and appends it to the current state at time
        `time` + the most recent time
        '''
        if len(state) != self.n_states:
            raise ValueError("Dimension of state and number of states must match!")
        self.time.append(self.time[-1] + time)
        self.state.append(state)
    
    
    def __str__(self) -> str:
        return (f"{repr(self)} with properties:\n" + 
                f"   entity_info: {repr(self.entityinfo)}\n"
                f"   n_states:    {self.n_states}\n")
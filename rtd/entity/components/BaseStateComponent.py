from abc import ABCMeta, abstractmethod



class BaseStateComponent(metaclass=ABCMeta):
    def __init__(self):
        self.entityinfo = None
        self.n_states = None
        self.state = None
        self.time = None
    

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def get_state(self, time):
        pass
    
    @abstractmethod
    def random_init(self):
        pass
    
    @abstractmethod
    def commit_state_data(self, times, states):
        pass
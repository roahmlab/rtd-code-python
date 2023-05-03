from abc import ABCMeta, abstractmethod



class BaseInfoComponent(metaclass=ABCMeta):
    def __init__(self):
        self.dimension = None
    

    @abstractmethod
    def reset(self):
        pass
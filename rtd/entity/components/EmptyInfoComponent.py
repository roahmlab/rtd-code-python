from rtd.entity.components import BaseInfoComponent



class EmptyInfoComponent(BaseInfoComponent):
    def __init__(self):
        BaseInfoComponent.__init__(self)
        self.dimension = 2
    
    def reset(self):
        raise NotImplementedError
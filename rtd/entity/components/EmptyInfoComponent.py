from rtd.entity.components import BaseInfoComponent



class EmptyInfoComponent(BaseInfoComponent):
    def __init__(self):
        super().__init__()
        self.dimension = 2
    
    def reset(self):
        raise NotImplementedError
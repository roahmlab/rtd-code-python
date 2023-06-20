from rtd.entity.components import BaseInfoComponent



class EmptyInfoComponent(BaseInfoComponent):
    '''
    An empty Info Component which should only ever
    be used as default values for info properties or
    for testing purposes
    '''
    def __init__(self):
        BaseInfoComponent.__init__(self)
        self.dimension = 2
    
    
    def reset(self):
        pass
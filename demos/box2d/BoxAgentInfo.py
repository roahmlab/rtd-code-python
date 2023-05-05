from rtd.entity.components import BaseInfoComponent
from rtd.util.mixins import Options



class BoxAgentInfo(BaseInfoComponent, Options):
    '''
    An info class that stores the agent's width,
    height, and color.
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "width": 1,
            "height": 1,
            "color": [1, 0, 1],
        }
    
    
    def __init__(self, **options):
        BaseInfoComponent.__init__(self)
        Options.__init__(self)
        self.mergeoptions(options)
        self.dimension = 2
        
        # initialize
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.width = options["width"]
        self.height = options["height"]
        self.color = options["color"]
    
    
    def __str__(self) -> str:
        '''
        Override string representation
        '''
        return (f"{repr(self)} with properties:\n" + 
                f"\twidth:  {self.width}\n" +
                f"\theight: {self.height}\n" +
                f"\tcolor:  {self.color}\n")
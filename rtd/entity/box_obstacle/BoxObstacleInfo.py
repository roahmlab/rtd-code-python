from rtd.entity.components import BaseInfoComponent
from rtd.util.mixins import Options



class BoxObstacleInfo(BaseInfoComponent, Options):
    '''
    An info component that stores the agent's dimensions
    and color
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "dims": [0, 0, 0],
            "color": [1, 0, 1],
        }
    
    
    def __init__(self, **options):
        # initialize base classes
        BaseInfoComponent.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.dimension = 3
        self.reset()
    
    
    def reset(self, **options):
        options = self.mergeoptions(options)
        self.dims: list[float, float, float] = options["dims"]
        self.color: list[float, float, float] = options["color"]
    
    
    def __str__(self) -> str:
        '''
        Override string representation
        '''
        return (f"{repr(self)} with properties:\n" + 
                f"   dims:  {self.dims}\n" +
                f"   color:  {self.color}\n")
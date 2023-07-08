class WorldState:
    '''
    This should hold atomic state instances of the world. Whether it is a
    predicted state or a measured state, it holds those relevant
    parameters that evolve over time for our code.
    '''
    def __init__(self):
        self.obstacles = None
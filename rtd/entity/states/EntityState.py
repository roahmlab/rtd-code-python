class EntityState:
    '''
    The state of a generic robot at a point in time, which is saved
    '''
    def __init__(self):
        self.time: list[float] = None
        # Any relevant robot properties that evolve over time
        self.state = None
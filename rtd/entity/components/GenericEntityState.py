from rtd.entity.components import BaseStateComponent, EmptyInfoComponent
from rtd.util.mixins import Options


class GenericEntityState(BaseStateComponent, Options):
    def __init__(self):
        super().__init__()  # initialize base classes
        self.entityinfo = EmptyInfoComponent
        
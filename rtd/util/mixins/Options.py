from abc import ABCMeta, abstractmethod



class Options(metaclass=ABCMeta):
    '''
    The Options mixin introduces an `instanceOptions` property which holds
    a dict of all sorts of configuration options. It also includes utility
    code for the merging of these dicts. This mixin requires you to write
    a static `defaultoptions` method.
    '''
    @staticmethod
    @abstractmethod
    def defaultoptions() -> dict:
        '''
        Abstract static method which needs to be implemented to provide
        the default options for any given class. Should return a dict.
        '''
        pass
    
    
    def __init__(self):
        '''
        This default constructor is run for any classes that inherit
        from this mixin. It will call the required `defaultoptions()`
        static function and create the initial `instanceOptions`
        '''
        # a dictionary that holds the configuration options
        self._instanceOptions = self.defaultoptions()
    
    
    def mergeoptions(self, newOptions: dict | list[dict]) -> dict:
        '''
        Takes in an option or a list of options and updates the current
        `instanceOptions`. Returns a copy of the updated `instanceOptions`
        '''
        if type(newOptions) is dict:
            self._instanceOptions.update(newOptions)
        else:
            [self._instanceOptions.update(optionDict) for optionDict in newOptions]
        return self.getoptions()

    
    def getoptions(self) -> dict:
        '''
        Returns a copy of the current `instanceOptions`
        '''
        return self._instanceOptions.copy();
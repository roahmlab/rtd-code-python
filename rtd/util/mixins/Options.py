from abc import ABCMeta, abstractmethod



class Options(metaclass=ABCMeta):
    '''
    This mixin adds functionality for easy configuration of complex objects.

    The Options mixin introduces an `instanceOptions` property which holds
    a dict of all sorts of configuration options. It also includes utility
    code for the merging of these dicts. This mixin requires you to write
    a static `defaultoptions` method.

    --- More Info ---
    Original Author (matlab): Adam Li (adamli@umich.edu)
    Author: Rei Meguro (rmeguro@umich.edu)
    Written: 2023-05-02
    Last Revised: 2023-05-2 (Rei Meguro)
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
        Constructs the Options mixin.
        
        This default constructor is run for any classes that inherit
        from this mixin. It will call the required `defaultoptions()`
        static function and create the initial `instanceOptions`.
        '''
        # a dictionary that holds the configuration options
        self.instanceOptions = self.defaultoptions()
    
    
    def mergeoptions(self, newOptions: list[dict] = []) -> dict:
        '''
        Merge in any number of option dicts
        
        This method merges any number of new option dicts into the
        `instanceOptions` property with an optional return of a copy
        of the `instanceOptions` dict.
        
        Arguments:
            newOptions (repeating): Dict with the configuration options to merge into the current `instanceOptions`.
        
        Returns:
            dict: Optional copy of the merged `instanceOptions`.
        '''
        # go through each of the options and merge them, merging any
        # substructs of needed.
        if type(newOptions) is not list:
            self.instanceOptions.update(newOptions)
        else:
            [self.instanceOptions.update(optionDict) for optionDict in newOptions]
        return self.instanceOptions

    
    def getoptions(self) -> dict:
        '''
        Returns the current `instanceOptions`
        
        This function can be overloaded to change how the
        `instanceOptions` are returned if desired.
        
        Returns:
            dict: Copy of the current `instanceOptions`.
        '''
        return self.instanceOptions;
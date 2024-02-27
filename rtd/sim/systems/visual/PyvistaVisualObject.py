from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod
from rtd.functional.sequences import toSequence

if TYPE_CHECKING:
    from pyvista import Actor



class PyvistaVisualObject(metaclass=ABCMeta):
    '''
    An object that can be extended to control the
    rendering of an entity
    '''
    @abstractmethod
    def create_plot_data(self, **options) -> Actor | list[Actor]:
        '''
        Abstract method which needs to be implemented to generate
        and return the plot data
        
        Parameters
        ----------
        **options
            options for creating the plot data
        
        Returns
        -------
        plot_obj : Actor | list[Actor]
            Pyvista actor(s) to plot
        '''
        pass

    
    @abstractmethod
    def plot(self, **options):
        '''
        Abstract method which needs to be implemented to update
        the generated plot data
        '''
        pass
    
    
    def __init__(self):
        # a pyvista actor object
        self.plot_data: Actor | list[Actor] = None
    
    
    def isPlotDataValid(self) -> bool:
        '''
        Checks if plot_data is a pyvista actor object
        
        Returns
        -------
        is_valid : bool
            whether the plot_data is a valid Pyvista actor
        '''
        return issubclass(type(toSequence(self.plot_data)[0]), Actor)
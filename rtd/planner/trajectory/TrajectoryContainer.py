from rtd.planner.trajectory import Trajectory
from rtd.entity.states import EntityState
import numpy as np
from nptyping import NDArray


class BadTrajectoryException(Exception):
    def __init__(self, message: str = ""):
        super().__init__(message)


class TrajectoryContainer:
    def __init__(self):
        # vector of start times for each trajectory
        # last element is always inf to ensure the last trajectory is always used
        self._startTimes: NDArray[float] = np.array([np.inf], np.float)
        
        # list of trajectories corresponding to the start times
        self._trajectories: NDArray[Trajectory] = np.array([], dtype=Trajectory)
    
    
    def setInitialTrajectory(self, initialTrajectory: Trajectory):
        '''
        Sets the initial trajectory for the container.
        This method must be called before any other method is called.
        
        Parameters
        ----------
        initialTrajectory : Trajectory
            the initial trajectory to add
        '''
        if initialTrajectory.startState != 0:
            raise BadTrajectoryException("Provided initial trajectory does not start at 0!")
        if not initialTrajectory.validate():
            raise BadTrajectoryException("Provided initial trajectory is invalid!")
        
        if not self.isValid(False):
            self._startTimes = np.array([initialTrajectory.startTime, np.inf], dtype=float)
            self._trajectories = np.array([initialTrajectory], dtype=Trajectory)
        else:
            self._startTimes[0] = initialTrajectory.startTime
            self._trajectories[0] = initialTrajectory
    
    
    def clear(self):
        '''
        Clears the container and resets it to the initial state
        It's expected that there's already some initial trajectory set.
        If not, a warning is thrown.
        '''
        if self.isValid():
            self._startTimes = np.array([0, np.inf], np.float)
            self._trajectories = np.array([self._trajectories[0]], dtype=Trajectory)
        else:
            print("Warning: clear() for TrajectoryContainer was called before valid initial trajectory was set!")
    
    
    def isValid(self, errorIfInvalid: bool = False):
        '''
        Checks if the container is valid.
        
        Parameters
        ----------
        errorIfInvalid : bool
            whether to raise an error when the container is invalid
        
        Returns
        -------
        valid : bool
            whether the container is valid or not
        '''
        valid = len(self._trajectories)>=1 and len(self._startTimes)==1+len(self._trajectories)
        if not valid and errorIfInvalid:
            raise BadTrajectoryException("Initial trajectory for the container has not been set!")
        return valid

    
    def setTrajectory(self, trajectory: Trajectory, errorIfInvalid: bool = False):
        '''
        Sets a new trajectory for the container to the end.
        The new trajectory must start at a time greater than equal to
        the end of the last trajectory.
        
        Parameters
        ----------
        trajectory : Trajectory
            the trajectory to add
        errorIfInvalid : bool
            whether to raise an error when the trajectory is invalid
        '''
        self.isValid(True)
        
        # add the trajectory if it is valid
        if trajectory.validate() and trajectory.startTime>=self._startTimes[-2]:
            self._startTimes[-1] = trajectory.startTime
            np.append(self._startTimes, np.inf)
            np.append(self._trajectories, trajectory)
        elif errorIfInvalid:
            raise BadTrajectoryException("Provided trajectory starts before the end of the last trajectory!")
        else:
            print("Warning: Invalid trajectory provided to TrajectoryContainer")
    
    
    def getCommand(self, time: float | list[float]) -> EntityState:
        '''
        Generates a command based on the time.
        The command is generated based on the trajectory that is active
        at the time. If the time is before the start of the first trajectory,
        then the command is generated based on the initial trajectory. If the
        time is after the last trajectory, then the command is generated based
        on the last trajectory. 
        
        Parameters
        ----------
        time : float | list[float]
            the time(s) to generate the command for
        
        Returns
        -------
        commands : bool
            the generated commands
        '''
        time = np.array(time)
        self.isValid(True)
        
        # generate an output trajectory based on the provided time
        ncommands = len(time)
        commands = np.empty(ncommands, dtype=EntityState)
        commands[-1] = self._trajectories[0].getCommand(0)
        
        for i in range(ncommands-1):
            mask = np.logical_and(time>=self._startTimes[i], time<=self._startTimes[i+1])
            if np.sum(mask) == 0:
                continue
            elif self._trajectories[i].vectorized:
                commands[mask] = self._trajectories[i].getCommand(time[mask])
            else:
                commands[mask] = (self._trajectories[j].getCommand(time[j]) for j in np.argwhere(mask).T[0])
        
        return commands
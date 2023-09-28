from typing import Iterator, Iterable



def toSequence(obj) -> Iterable:
    '''
    Converts single elements into lists to make it easier
    to handle either a single input or a list of inputs
    
    e.g. 
    [1, 2, 3] -> [1, 2, 3]
    ("a", "b") -> ("a", "b")
    1 -> [1]
    '''
    return obj if hasattr(obj, '__iter__') else [obj]



def arrange(start: float, end: float, step: float) -> Iterator[float]:
    '''
    Creates a generator from `start` (inclusive) to `end`
    (exclusive) with step size `step`
    '''
    count = int((end - start) // step) + 1
    return (start + i*step for i in range(count))



def arrange_list(start: float, end: float, step: float) -> list[float]:
    '''
    Creates a list from `start` (inclusive) to `end`
    (exclusive) with step size `step`
    '''
    count = int((end - start) / step) + 1
    return [start + i*step for i in range(count)]
def toSequence(obj) -> list | tuple:
    '''
    Converts single elements into lists to make it easier
    to handle either a single input or a list of inputs
    
    e.g. 
    [1, 2, 3] -> [1, 2, 3]
    ("a", "b") -> ("a", "b")
    "hello" -> "hello"
    1 -> [1]
    '''
    return obj if type(obj) in (list, tuple) else [obj]



def arrange(start: float, end: float, step: float):
    '''
    Creates a generator from `start` (inclusive) to `end`
    (exclusive) with step size `step`
    '''
    count = int((end - start) // step) + 1
    return (start + i*step for i in range(count))



def arrange_list(start: float, end: float, step: float):
    '''
    Creates a list from `start` (inclusive) to `end`
    (exclusive) with step size `step`
    '''
    count = int((end - start) // step) + 1
    return [start + i*step for i in range(count)]
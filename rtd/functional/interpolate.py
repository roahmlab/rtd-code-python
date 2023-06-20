from bisect import bisect, bisect_left



def interp1(x: list[float], y: list[float], x_at: float) -> list[float]:
    '''
    This takes the lists `x` and `y`, and returns the interpolated
    y value at `x_at`. Length of `x` and `y` must be equal, `x` must
    be sorted and `x_at must` be a single value. Interpolation type is
    linear

    E.g.,
    x=[0, 2, 6, 10]
    y=[4,16, 8, 0]

    interp1(x,y, 0)  = 4
    interp1(x,y, 1)  = 10
    interp1(x,y, 2)  = 16
    interp1(x,y, 4)  = 12
    interp1(x,y, 7)  = 6
    interp1(x,y, 12) = 0
    '''
    # find closest point to left and right
    i_left = max(0, bisect(x, x_at)-1)
    i_right = min(len(x)-1, bisect_left(x, x_at))
    
    if i_left == i_right:
        return y[i_left]
    ratio = (x_at - x[i_left]) / (x[i_right] - x[i_left])
    return y[i_left] + ratio*(y[i_right] - y[i_left])


def interp1_list(x: list[float], y: list[list[float]], x_at: float) -> list[float]:
    '''
    Same as interp1 but broadcasts it to each element in `y`
    
    E.g.,
    x=[2, 4, 8]
    y=[[1, 1], [2, 4], [10, 0]]

    interp1(x,y, 0)  = [1, 1]
    interp1(x,y, 4)  = [2, 4]
    interp1(x,y, 5)  = [4, 3]
    interp1(x,y, 10) = [10, 0]
    '''
    # find closest point to left and right
    i_left = max(0, bisect(x, x_at)-1)
    i_right = min(len(x)-1, bisect_left(x, x_at))
    
    if i_left == i_right:
        return y[i_left]
    ratio = (x_at - x[i_left]) / (x[i_right] - x[i_left])
    return [y[i_left][j] + ratio*(y[i_right][j] - y[i_left][j])
            for j in range(len(y[0]))]
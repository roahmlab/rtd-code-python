from nptyping import NDArray, Shape, Float

# 1D float vector
Vecnp = NDArray[Shape['N'], Float]      #: 1D NDArray
Vec = list[float] | Vecnp               #: 1D list or NDArray

# Bounds
Boundsnp = NDArray[Shape['2,N'], Float] #: list of bounds (a 2-row NDArray)
Bound = list[float, float]              #: pair of min and max bounds
Bounds = list[Bound] | Boundsnp         #: list of bounds (a 2-row list or NDArray)

# Matrix
Matnp = NDArray[Shape['N,M'], Float]    #: 2D NDArray
Mat = list[list[float]] | Matnp         #: 2D list of NDArray
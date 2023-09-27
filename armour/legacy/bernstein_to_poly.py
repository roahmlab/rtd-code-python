from math import comb
import numpy as np



def bernstein_to_poly(beta: list[float], n: int):
    '''
    converts bernstein polynomial coefficients to
    monomial coefficients
    '''
    alphas = np.empty_like(beta)
    deg = len(beta)-1
    # All inclusive loops
    for i in range(n):
        alphas[i] = 0.0
        for j in range(i+1):
            alphas[i] = alphas[i] \
                + (-1.0)**(i-j) \
                * float(comb(deg, i)) \
                * float(comb(i, j)) \
                * beta[j]
    return alphas
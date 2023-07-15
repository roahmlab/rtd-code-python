from math import comb



def bernstein_to_poly(beta: list[float], n: int):
    '''
    converts bernstein polynomial coefficients to
    monomial coefficients
    '''
    return [sum([(-1)**(i-j)*comb(n, i)*comb(i, j)*beta[j] for j in range(i)]) for i in range(n)]
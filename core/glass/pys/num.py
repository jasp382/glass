"""
Spatial Numpy Tools
"""

import numpy

def count_where(vector, condition):
    """
    Count the cells with some value
    """
    extraction = len(list(numpy.extract(condition, vector)))
    return extraction


def distance_line_point(lx1, ly1, lx2, ly2, px, py):
    """
    Calculate near distance between a line and a point
    """
    
    import numpy as np
    
    p1 = np.array([lx1, ly1])
    p2 = np.array([lx2, ly2])
    p3 = np.array([px, py])
    
    distance = np.linalg.norm(
        np.cross(p2-p1, p1-p3))/np.linalg.norm(p2-p1)
    
    return distance


def get_minmax_fm_seq_values(a):
    """
    Return Minimum and Maximum values from sequential values in array

    For this input array:
    a = [ 1  8  9 10 11 12 13 14 15 22 23 24 25]
    The result will be:
    b = [[1, 1], [8, 15], [22, 25]]
    """

    import numpy as np

    b = np.array(np.split(a, np.where(np.diff(a) != 1)[0]+1))

    min_b = np.array([[np.amin(_b)] for _b in b])
    max_b = np.array([[np.amax(_b)] for _b in b])

    return np.hstack((min_b, max_b))

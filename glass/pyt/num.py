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


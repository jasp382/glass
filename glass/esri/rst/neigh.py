"""
Neighborhood toolset
"""

import arcpy

from arcpy.sa import *

def focal_statistics(irst, orst, neigh_type, neigh_val, statistic):
    """
    Run Focal statistics

    neigh_type:
    - Annulus
    - Circle
    - Rectangle
    - Wedge
    - Irregular
    - Weight
    """

    if neigh_type == 'Annulus':
        neigh = NbrAnnulus(neigh_val[0], neigh_val[1], 'CELL')
    
    else:
        neigh = NbrRectangle(neigh_val[0], neigh_val[1], 'CELL')
    
    ofocal = FocalStatistics(irst, neigh, statistic, "NODATA")

    ofocal.save(orst)

    return orst


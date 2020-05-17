"""
Execute cheese buffer tool as 
ArcGIS Pro Python Script
"""

import arcpy
from glass.gp.prox.bfing import cheese_buffer

i_shp = arcpy.GetParameterAsText(0)
bdist = arcpy.GetParameterAsText(1)
intvl = arcpy.GetParameterAsText(2)
o_shp = arcpy.GetParameterAsText(3)
epsg  = arcpy.GetParameterAsText(4)

cheese_buffer(i_shp, int(bdist), int(intvl), o_shp, epsg=int(epsg))


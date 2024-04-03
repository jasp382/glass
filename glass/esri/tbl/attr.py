"""
Record Geometric Properties in some Table
"""

import arcpy


def geom_attr_to_shp(lyr, field_name, geom_attr="AREA", srs="",
                  area_unit="SQUARE_METERS", lenunit=None):
    """
    Add Geometry Attribute to table
    """

    area_unit = None if lenunit else area_unit

    nlyr = arcpy.management.CalculateGeometryAttributes(
        lyr,
        geometry_property=[[field_name, geom_attr]],
        area_unit=area_unit,
        length_unit=lenunit,
        coordinate_system=srs
    )[0]
    
    return nlyr


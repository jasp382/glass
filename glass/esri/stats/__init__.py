"""
Data Statistics
"""

import arcpy

def summary(inTbl, outTbl, fields_stat):
    """
    Statistics analysis tool of ArcGIS toolbox
    
    Available statistics types are:
    * SUM   - Adds the total value for the specified field. 
    * MEAN  - Calculates the average for the specified field. 
    * MIN   - Finds the smallest value for all records of the specified field. 
    * MAX   - Finds the largest value for all records of the specified field. 
    * RANGE - Finds the range of values (MAX minus MIN) for the specified field. 
    * STD   - Finds the standard deviation on values in the specified field.
    * COUNT - Finds the number of values included in statistical calculations.
    This counts each value except null values. To determine the number of null
    values in a field, use the COUNT statistic on the field in question,
    and a COUNT statistic on a different field which does not contain nulls
    (for example, the OID if present), then subtract the two values.
    * FIRST - Finds the first record in the Input Table and uses its
    specified field value. 
    * LAST  - Finds the last record in the Input Table and uses its
    specified field value.
    """
    
    arcpy.Statistics_analysis(
        in_table=inTbl, out_table=outTbl, 
        statistics_fields=fields_stat
    )
    
    return outTbl

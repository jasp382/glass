"""
Columns
"""

import arcpy


def add_col(tbl, name, fld_type, length, precision=""):
    """
    Add new column to table
    """

    nlyr = arcpy.management.AddField(
        in_table=tbl, field_name=name,
        field_type=fld_type, field_length=length
    )[0]

    return nlyr



def cols_calc(table, fld, expression, newcols=None, code=None):
    """
    Field Calculator
    
    newcols = {
        "TYPE" : "DOUBLE", "LENGTH" : "10", "PRECISION" : "3"
    }
    """
    
    if newcols:
        table = add_col(
            table, fld, newcols["TYPE"],
            newcols["LENGTH"], newcols["PRECISION"]
        )

    nlyr = arcpy.management.CalculateField(
        in_table=table, field=fld,
        expression=expression,
        expression_type="PYTHON3",
        code_block=code
    )

    return nlyr


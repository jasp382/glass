
import arcpy


def dbf_to_view(dbf, viewn=None):
    """
    Dbf table to Table View
    """

    from glass.pys.oss import fprop

    n = fprop(dbf, 'fn') if not viewn or \
        type(viewn) != str else viewn
    
    view = arcpy.MakeTableView_management(dbf, n)

    return n


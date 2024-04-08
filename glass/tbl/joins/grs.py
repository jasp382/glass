"""
Join Tables using GRASS GIS tools
"""


def join_table(shp, jshp, shpid, joinfk):
    """
    Join Tables using GRASS GIS
    """
    
    from glass.pys import execmd
    
    rcmd = execmd((
        f"v.db.join map={shp} column={shpid} "
        f"other_table={jshp} other_column={joinfk}"
    ))

    return shp


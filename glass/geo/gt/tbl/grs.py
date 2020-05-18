"""
GRASS GIS Tools for table management
"""

def update_table(shp, col, v, onde, lyrN=1, ascmd=None):
    """
    Update Table
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        fc = Module(
            'v.db.update', map=shp, column=col, value=v, where=onde,
            layer=lyrN, run_=False, quiet=True
        )
        fc()
    
    else:
        from glass.pyt import execmd
        
        rcmd = execmd((
            "v.db.update map={} column={} value=\"{}\" where={} "
            "layer={} --quiet"
        ).format(
            shp, col, v, onde, str(lyrN)
        ))


def add_table(shp, fields, lyrN=1, asCMD=None):
    """
    Create table on the GRASS GIS Sqlite Database
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        add = Module(
            "v.db.addtable", map=shp, columns=fields, layer=lyrN, quiet=True
        )
    
    else:
        from glass.pyt import execmd
        
        rcmd = execmd((
            "v.db.addtable map={}{} layer={} --quiet"
        ).format(
            shp,
            "" if not fields else " columns=\"{}\"".format(fields),
            str(lyrN)
        ))


def del_table(shp):
    """
    Delete table from GRASS GIS Sqlite Database
    """
    
    from grass.pygrass.modules import Module
    
    deltable = Module(
        "v.db.droptable", map=shp, flags='f', run_=False, quiet=True
    )
    
    deltable()


def reset_table(table, new_flds, values2write, whr_fields=None):
    """
    Delete table; create new table and update it
    """
    
    if type(new_flds) != dict:
        raise ValueError("new_flds must be a dict")
    
    if type(values2write) != dict:
        raise ValueError("values2write must be a dict")
    
    if whr_fields and type(whr_fields) != dict:
        raise ValueError("whr_fields must be a dict")
    
    del_table(table)
    add_table(table, ', '.join([
        '{} {}'.format(f, new_flds[f]) for f in new_flds]))
    
    for f in values2write:
        update_table(
            table, f, values2write[f],
            '{} IS NULL'.format(f) if not whr_fields else \
                '{} IS NULL'.format(f) if f not in whr_fields else \
                whr_fields[f]
        )

def add_and_update(table, new_flds, val_to_write):
    """
    Create new table and put some values in it
    """
    
    if type(new_flds) != dict:
        raise ValueError("new_flds must be a dict")
    
    if type(val_to_write) != dict:
        raise ValueError("values2write must be a dict")
    
    add_table(table, ", ".join([
        '{} {}'.format(f, new_flds[f]) for f in new_flds
    ]))
    
    for fld in val_to_write:
        update_table(
            table, fld, val_to_write[fld],
            "{} IS NULL".format(fld), ascmd=None
        )

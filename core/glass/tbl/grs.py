"""
GRASS GIS Tools for table management
"""


def add_table(shp, fields, lyrN=1, asCMD=None, keyp=None):
    """
    Create table on the GRASS GIS Sqlite Database
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        add = Module(
            "v.db.addtable", map=shp, columns=fields,
            key=keyp if keyp else 'cat',
            layer=lyrN, quiet=True
        )
    
    else:
        from glass.pys import execmd

        cols = '' if not fields else f' columns=\"{fields}\"'
        keyv = '' if not keyp else f' key={keyp}'
        
        rcmd = execmd((
            f"v.db.addtable map={shp}{keyv}"
            f"{cols} layer={str(lyrN)} --quiet"
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

    from glass.tbl.col import cols_calc
    
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
        cols_calc(
            table, f, values2write[f],
            f'{f} IS NULL' if not whr_fields else \
                f'{f} IS NULL' if f not in whr_fields else \
                whr_fields[f]
        )


def add_and_update(table, new_flds, val_to_write):
    """
    Create new table and put some values in it
    """

    from glass.tbl.col import cols_calc
    
    if type(new_flds) != dict:
        raise ValueError("new_flds must be a dict")
    
    if type(val_to_write) != dict:
        raise ValueError("values2write must be a dict")
    
    add_table(table, ", ".join([
        '{} {}'.format(f, new_flds[f]) for f in new_flds
    ]))
    
    for fld in val_to_write:
        cols_calc(
            table, fld, val_to_write[fld],
            f"{fld} IS NULL", ascmd=None
        )

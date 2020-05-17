"""
GIS Table Support
"""

def category(inShp, outShp, useOption, LyrN="1",
             geomType="point,line,boundary,centroid,area,face,kernel",
             asCMD=None):
    """
    v.category attaches, copies, deletes or reports categories of vector
    geometry objects. Further on, v.category adds a number given by the
    cat option to categories of the selected layer. These categories (IDs)
    are used to assign IDs or to group geometry objects into categories
    (several different geometry objects share the same category).
    These categories are also used to link geometry object(s) to attribute
    records (from an attribute table linked to vector map).
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
    
        vcat = Module(
            "v.category", input=inShp, layer=LyrN, type=geomType,
            output=outShp, option=useOption, cat=1,
            overwrite=True, run_=False
        )
    
        vcat()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            f"v.category input={inShp} layer={LyrN} "
            f"type={geomType} output={outShp} "
            f"option={useOption} cat=1 --overwrite --quiet"
        ))
    
    return outShp


def merge_tbls(folder, out_tbl, tbl_format='.dbf'):
    """
    Merge all tables in folder into one single table
    """

    from glass.pys.oss    import lst_ff
    from glass.rd         import tbl_to_obj
    from glass.wt         import obj_to_tbl
    from glass.dtt.mge.pd import merge_df

    tbls = lst_ff(folder, file_format=tbl_format)

    tbls_dfs = [tbl_to_obj(t) for t in tbls]

    out_df = merge_df(tbls_dfs)

    obj_to_tbl(out_df, out_tbl)

    return out_tbl


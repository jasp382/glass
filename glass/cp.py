"""
Copy data from one place to another
"""

def copy_feat(inShp, outShp, gisApi='ogrlyr', outDefn=None, only_geom=None):
    """
    Copy Features to a new Feature Class
    """
    
    if gisApi == 'ogrlyr':
        """
        Copy the features of one layer to another layer...
    
        If the layers have the same fields, this method could also copy
        the tabular data
    
        TODO: See if the input is a layer or not and make arrangements
        """
        
        from osgeo import ogr
        
        for f in inShp:
            geom = f.GetGeometryRef()
        
            new = ogr.Feature(outDefn)
        
            new.SetGeometry(geom)
        
        # Copy tabular data
        if not only_geom:
            for i in range(0, outDefn.GetFieldCount()):
                new.SetField(outDefn.GetFieldDefn(i).GetNameRef(), f.GetField(i))
        
        outShp.CreateFeature(new)
        
        new.Destroy()
        f.Destroy()
        
        return None
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp


def copy_insame_vector(inShp, colToBePopulated, srcColumn, destinyLayer,
                       geomType="point,line,boundary,centroid",
                       asCMD=None):
    """
    Copy Field values from one layer to another in the same GRASS Vector
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        vtodb = Module(
            "v.to.db", map=inShp, layer=destinyLayer, type=geomType,
            option="query", columns=colToBePopulated,
            query_column=srcColumn, run_=False, quiet=True,
            overwrite=True
        )
    
        vtodb()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            f"v.to.db map={inShp} layer={destinyLayer} "
            f"type={geomType} option=query columns={colToBePopulated} "
            f"query_column={srcColumn} --quiet --overwrite"
        ))


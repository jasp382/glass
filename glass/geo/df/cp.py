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


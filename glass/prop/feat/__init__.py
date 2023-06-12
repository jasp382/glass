"""
Feature Classes Properties
"""


def feat_count(shp, gisApi='pandas', work=None, loc=None):
    """
    Count the number of features in a feature class
    
    API'S Available:
    * gdal;
    * arcpy;
    * pygrass;
    * pandas;
    """
    
    if gisApi == 'ogr':
        from osgeo        import ogr
        from glass.prop import drv_name
    
        data = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
        lyr = data.GetLayer()
        fcnt = int(lyr.GetFeatureCount())
        data.Destroy()
    
    elif gisApi == 'grass':
        if not work or not loc:
            raise ValueError((
                "If gisApi=='grass', work and loc must be defined!"
            ))
        
        import os
        from glass.prop.sql import row_num
        
        db = os.path.join(
            work, loc, 'PERMANENT', 'sqlite', 'sqlite.db'
        )

        fcnt = row_num(db, shp, api='sqlite')
    
    elif gisApi == 'pandas':
        from glass.rd.shp import shp_to_obj
        
        gdf = shp_to_obj(shp)
        
        fcnt = int(gdf.shape[0])
        
        del gdf
    
    else:
        raise ValueError(f'The api {gisApi} is not available')
    
    return fcnt


def featcnt_infolder(folder, geoformat='.shp'):
    """
    Read all shapes in folder and return total
    number of features in folder
    """

    from glass.rd.shp import shp_to_obj
    from glass.pys.oss import lst_ff

    shps = lst_ff(folder, file_format=geoformat)

    nfeat = []
    for s in shps:
        df = shp_to_obj(s)

        nfeat.append(df.shape[0])
    
    return sum(nfeat)


def get_gtype(shp, name=True, py_cls=None, geomCol="geometry",
              gisApi='pandas'):
    """
    Return the Geometry Type of one Feature Class or GeoDataFrame
    
    API'S Available:
    * ogr;
    * pandas;
    """
    
    if gisApi == 'pandas':
        from glass.prop.gpd import geom_type
        from pandas import DataFrame
        
        if not isinstance(shp, DataFrame):
            from glass.rd.shp import shp_to_obj
            
            gdf     = shp_to_obj(shp)
            geomCol = "geometry"
        
        else:
            gdf = shp
        
        return geom_type(gdf, geomCol)
    
    elif gisApi == 'ogr':
        from osgeo      import ogr
        from glass.prop import drv_name
        
        geom_types = {
            "POINT"           : ogr.wkbPoint,
            "MULTIPOINT"      : ogr.wkbMultiPoint,
            "LINESTRING"      : ogr.wkbLineString,
            "MULTILINESTRING" : ogr.wkbMultiLineString,
            "POLYGON"         : ogr.wkbPolygon,
            "MULTIPOLYGON"    : ogr.wkbMultiPolygon
        }
        
        d = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
        l = d.GetLayer()
        gtype = l.GetGeomType()

        for g in geom_types:
            if gtype == geom_types[g]:
                gname = g; gcls = geom_types[g]
                break
        
        d.Destroy()
        del l
        
        return {gname: gcls} if name and py_cls else gname \
                if name and not py_cls else gcls \
                if not name and py_cls else None
    
    else:
        raise ValueError(f'The api {gisApi} is not available')


"""
Extent of Shapefiles and such
"""

def get_ext(shp):
    """
    Return extent of a Vectorial file
    
    Return a tuple object with the follow order:
    (left, right, bottom, top)
    
    API'S Available:
    * ogr;
    """
    
    gisApi = 'ogr'
    
    if gisApi == 'ogr':
        from osgeo        import ogr
        from glass.prop import drv_name
    
        dt = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
        lyr = dt.GetLayer()
        extent = lyr.GetExtent()
    
        dt.Destroy()
    
    return list(extent)


"""
Fields Information
"""

def lst_fld(shp):
    """
    Return a list with every field name in a vectorial layer
    """
    
    from osgeo           import ogr
    from glass.prop import drv_name
    
    if type(shp) == ogr.Layer:
        lyr = shp
        c=0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = data.GetLayer()
        c= 1
    
    defn = lyr.GetLayerDefn()
    
    fields = []
    for i in range(0, defn.GetFieldCount()):
        fdefn = defn.GetFieldDefn(i)
        fields.append(fdefn.name)
    
    if c:
        del lyr
        data.Destroy()
    
    return fields


"""
Geometric Properties
"""

def get_cntr_bnd(shp, isFile=None):
    """
    Return centroid (OGR Point object) of a Boundary (layer with a single
    feature).
    """
    
    from osgeo           import ogr
    from glass.prop import drv_name
    
    if isFile:
        shp = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = shp.GetLayer()
    
        feat = lyr[0]; geom = feat.GetGeometryRef()
    
    else:
        geom = shp
    
    centroid = geom.Centroid()
    
    cnt = ogr.CreateGeometryFromWkt(centroid.ExportToWkt())
    
    shp.Destroy()
    
    return cnt


def area_to_dic(shp):
    """
    Return the following output:
    
    dic = {
        id_feat: area,
        ...,
        id_feat: area
    }
    """
    
    from osgeo           import ogr
    from glass.prop import drv_name
    
    o = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
    l = o.GetLayer()
    d = {}
    c = 0
    for feat in l:
        g = feat.GetGeometryRef()
        area = g.GetArea()
        d[c] = area
        c += 1
    del l
    o.Destroy()
    return d


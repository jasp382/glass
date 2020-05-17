"""
Buffer Properties
"""

def get_buffer_radius(bfShp, isFile=None):
    """
    Return the radius of a buffer boundary in meters.
    
    The layer must be only one feature
    """
    
    from osgeo import ogr
    
    if isFile:
        bfshp = ogr.GetDriverByName(drv_name(bfShp)).Open(bfShp, 0)
    
        bfLyr = bfShp.GetLayer()
    
        feat = bfLyr[0]; geom = feat.GetGeometryRef()
    
    else:
        geom = ogr.CreateGeometryFromWkt(bfShp)
    
    center = geom.Centroid()
    c=0
    for pnt in geom:
        if c==1:
            break
        pnt_aux = pnt
        c+=1
    
    x_center, y_center = (center.GetX(), center.GetY())
    x_aux, y_aux = (pnt_aux.GetX(), pnt_aux.GetY())
    
    dist = (
        (pnt_aux.GetX() - x_center)**2 + (pnt_aux.GetY() - y_center)**2
    )**0.5
    
    del center
    if isFile:
        bfShp.Destroy()
    
    return round(dist, 0)


def bf_prop(buffer_shp, epsg_in, isFile=None):
    """
    Return the centroid and radius distance of one buffer geometry
    
    Centroid X, Y in the units of the buffer_shp;
    Radius in meters.
    
    Object return will be something like this:
    o = {
        'X': x_value,
        'Y': y_value,
        'R': radius_value
    }
    """
    
    from glass.prop.feat import get_cntr_bnd
    
    if isFile:
        from glass.tbl.filter import geom_by_idx
        
        BUFFER_GEOM = ogr.CreateGeometryFromWkt(
            geom_by_idx(buffer_shp, 0)
        )
    
    else:
        BUFFER_GEOM = ogr.CreateGeometryFromWkt(buffer_shp)
    
    # Get x_center, y_center and dist from polygon geometry
    # TODO: Besides 4326, we need to include also the others geographic systems
    if int(epsg_in) == 4326:
        from glass.prj.obj import prj_ogrgeom
        
        BUFFER_GEOM_R = prj_ogrgeom(BUFFER_GEOM, epsg_in, 3857)
    
    else:
        BUFFER_GEOM_R = BUFFER_GEOM
    
    dist   = get_buffer_radius(BUFFER_GEOM_R.ExportToWkt(), isFile=None)
    center = get_cntr_bnd(BUFFER_GEOM, isFile=None)
    
    return {
        'X': center.GetX(), 'Y': center.GetY(), 'R': dist
    }


def getBufferParam(inArea, inAreaSRS, outSRS=4326):
    """
    Get Buffer X, Y Center and radius in any SRS (radius in meteres).
    
    Check the type of the 'inArea' Object and return the interest values.
    
    inArea could be a file, dict, list or tuple
    """
    
    import os; from osgeo  import ogr
    from glass.gobj   import new_pnt
    from glass.prj.obj import prj_ogrgeom
    
    TYPE = type(inArea)
    
    if TYPE == str:
        # Assuming that inArea is a file
        
        # Check if exists
        if os.path.exists(inArea):
            if os.path.isfile(inArea):
                from glass.tbl.filter import geom_by_idx
                
                # Get Geometry object
                BUFFER_GEOM = geom_by_idx(inArea, 0)
                
                # To outSRS
                if int(inAreaSRS) != outSRS:
                    BUFFER_GEOM = prj_ogrgeom(
                        ogr.CreateGeometryFromWkt(BUFFER_GEOM),
                        inAreaSRS, outSRS
                    ).ExportToWkt()
                
                # Get x_center, y_center and radius
                xyr = bf_prop(BUFFER_GEOM, outSRS, isFile=None)
                x_center, y_center, dist = str(
                    xyr['X']), str(xyr['Y']), str(xyr['R'])
            
            else:
                raise ValueError(
                    'The given path exists but it is not a file'
                )
    
        else:
            raise ValueError('The given path doesn\'t exist')
    
    elif TYPE == dict:
        X = 'x' if 'x' in inArea else 'X' if 'X' in inArea else \
            'lng' if 'lng' in inArea else None
        
        Y = 'y' if 'x' in inArea else 'Y' if 'Y' in inArea else \
            'lat' if 'lat' in inArea else None
        
        R = 'r' if 'r' in inArea else 'R' if 'R' in inArea else \
            'rad' if 'rad' in inArea else 'RADIUS' if 'RADIUS' in inArea \
            else 'radius' if 'radius' in inArea else None
        
        if not X or not Y or not R:
            raise ValueError((
                'The keys used to identify the buffer properties '
                'are not valid! '
                'Please choose one of the following keys groups: '
                'x, y, r; '
                'X, Y, R; '
                'lat, lng, rad'
            ))
        
        else:
            x_center, y_center, dist = (
                str(inArea[X]), str(inArea[Y]), str(inArea[R])
            )
            
            if inAreaSRS != outSRS:
                pnt_wgs = prj_ogrgeom(
                    new_pnt(x_center, y_center), inAreaSRS, outSRS)
                
                x_center, y_center = (pnt_wgs.GetX(), pnt_wgs.GetY())
    
    elif TYPE == list or TYPE == tuple:
        x_center, y_center, dist = inArea
        
        if inAreaSRS != outSRS:
            pnt_wgs = prj_ogrgeom(
                new_pnt(x_center, y_center), inAreaSRS, outSRS
            )
            
            x_center, y_center = (pnt_wgs.GetX(), pnt_wgs.GetY())
    
    else:
        raise ValueError((
            'Please give a valid path to a shapefile or a tuple, dict or '
            'list with the x, y and radius values'
        ))
    
    return x_center, y_center, dist


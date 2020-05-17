"""
Spatial Reference Systems Properties
"""

from osgeo import osr

def get_trans_param(in_epsg, out_epsg, export_all=None):
    """
    Return transformation parameters for two Spatial Reference Systems
    """
    
    i = osr.SpatialReference()
    i.ImportFromEPSG(in_epsg)
    o = osr.SpatialReference()
    o.ImportFromEPSG(out_epsg)
    t = osr.CoordinateTransformation(i, o)
    if not export_all:
        return t
    else:
        return {'input': i, 'output': o, 'transform': t}


def epsg_to_wkt(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s.ExportToWkt()


def get_sref_from_epsg(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s


def get_shp_sref(shp):
    """
    Get Spatial Reference Object from Feature Class/Lyr
    """
    
    from osgeo        import ogr
    from glass.prop import drv_name
    
    if type(shp) == ogr.Layer:
        lyr = shp
        
        c = 0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp)
        
        lyr = data.GetLayer()
        c = 1
    
    spref = lyr.GetSpatialRef()
    
    if c:
        del lyr
        data.Destroy()
    
    return spref


def get_gml_epsg(gmlFile):
    """
    Get EPSG of GML File
    """
    
    from xml.dom import minidom
    
    geomTag = [
        'gml:Polygon', 'gml:MultiPolygon', 
        'gml:Point', 'gml:MultiPoint',
        'gml:LineString', 'gml:MultiLineString'
    ]
    
    # Open XML
    xmlDoc = minidom.parse(gmlFile)
    
    epsgValue = None
    for geom in geomTag:
        if epsgValue:
            break
        
        xmlNodes = xmlDoc.getElementsByTagName(geom)
        
        if not xmlNodes:
            continue
        
        epsgValue = xmlNodes[0].attributes["srsName"].value.split(':')[1]
    
    return epsgValue


def get_shp_epsg(shp, returnIsProj=None):
    """
    Return EPSG code of the Spatial Reference System of a Feature Class
    """
    
    from glass.pys.oss import fprop
    
    if fprop(shp, 'ff') != '.gml':
        proj = get_shp_sref(shp)
    else:
        epsg = get_gml_epsg(shp)
        
        if not epsg:
            raise ValueError(
                '{} file has not Spatial Reference assigned!'.format(shp)
            )
        
        proj = get_sref_from_epsg(int(epsg))
    
    if not proj:
        raise ValueError(
            '{} file has not Spatial Reference assigned!'.format(shp)
        )
    
    epsg = int(str(proj.GetAttrValue('AUTHORITY', 1)))
    
    if not returnIsProj:
        return epsg
    else:
        if proj.IsProjected:
            mod_proj = proj.GetAttrValue(str('projcs'))
            
            if not mod_proj:
                return epsg, None
            else:
                return epsg, True
        
        else:
            return epsg, None


"""
Raster Spatial Reference Systems
"""

def get_rst_epsg(rst, returnIsProj=None):
    """
    Return the EPSG Code of the Spatial Reference System of a Raster
    """
    
    import os
    from osgeo import gdal
    from glass.prop.img import rst_epsg
    
    if not os.path.exists(rst):
        raise ValueError((
            f"{rst} does not exist! Please give a valid "
            "path to a raster file"
        ))
    
    d = gdal.Open(rst)
    
    if not returnIsProj:
        epsg = rst_epsg(d, isproj=None)

        return epsg
    else:
        epsg, isproj = rst_epsg(d, isproj=True)

        return epsg, isproj


"""
Generic Methods
"""

def get_epsg(inFile):
    """
    Get EPSG of any GIS File
    """
    
    from glass.prop import check_isRaster, is_shp
    
    if check_isRaster(inFile):
        return get_rst_epsg(inFile)
    else:
        if is_shp(inFile):
            return get_shp_epsg(inFile)
        else:
            return None


def get_srs(in_file):
    """
    Get SRS Object of any GIS File
    """

    epsg = get_epsg(in_file)

    return None if not epsg else get_sref_from_epsg(epsg)


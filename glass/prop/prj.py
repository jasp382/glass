"""
Spatial Reference Systems Properties
"""

import os
from osgeo import gdal, osr, ogr


def trans_param(in_epsg, out_epsg, export_all=None):
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


def sref_from_epsg(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s


def shp_sref(shp, lyrn=None):
    """
    Get Spatial Reference Object from Feature Class/Lyr
    """
    
    from glass.prop.df import drv_name
    
    if type(shp) == ogr.Layer:
        lyr = shp
        
        c = 0
    
    else:
        drv = 'OpenFileGDB' if '.gdb' in shp else drv_name(shp)

        data = ogr.GetDriverByName(drv).Open(shp)
        
        lyr = data.GetLayer() if not lyrn \
            else data.GetLayer(lyrn)
        
        c = 1
    
    spref = lyr.GetSpatialRef()
    
    if c:
        del lyr
        data.Destroy()
    
    return spref


def gml_epsg(gmlFile):
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


def shp_epsg(shp, returnIsProj=None, lyrname=None):
    """
    Return EPSG code of the Spatial Reference System of a Feature Class
    """
    
    from glass.pys.oss import fprop
    
    if fprop(shp, 'ff') != '.gml':
        proj = shp_sref(shp, lyrn=lyrname)
    else:
        epsg = gml_epsg(shp)
        
        if not epsg:
            raise ValueError(f'{shp} file has not Spatial Reference assigned!')
        
        proj = sref_from_epsg(int(epsg))
    
    if not proj:
        raise ValueError(f'{shp} file has not Spatial Reference assigned!')
    
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

def rst_epsg(rst, returnIsProj=None):
    """
    Return the EPSG Code of the Spatial Reference System of a Raster
    """
    
    from glass.prop.img import rst_epsg as repsg
    
    if not os.path.exists(rst):
        raise ValueError((
            f"{rst} does not exist! Please give a valid "
            "path to a raster file"
        ))
    
    d = gdal.Open(rst)
    
    if not returnIsProj:
        epsg = repsg(d, isproj=None)

        return epsg
    else:
        epsg, isproj = repsg(d, isproj=True)

        return epsg, isproj


"""
Generic Methods
"""

def get_epsg(inFile, is_proj=None, lyrname=None):
    """
    Get EPSG of any GIS File
    """
    
    from glass.prop.df import is_rst, is_shp

    irst, ishp = is_rst(inFile), is_shp(inFile)
    
    if irst and not ishp:
        return rst_epsg(inFile, returnIsProj=is_proj)
    
    elif not irst and ishp:
        return shp_epsg(
            inFile,
            returnIsProj=is_proj,
            lyrname=lyrname
        )
    
    else:
        return None


def get_srs(in_file):
    """
    Get SRS Object of any GIS File
    """

    epsg = get_epsg(in_file)

    return None if not epsg else sref_from_epsg(epsg)


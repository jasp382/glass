"""
From OpenStreetMap to Feature Class
"""

def osm_to_sqdb(osmXml, osmSQLITE):
    """
    Convert OSM file to SQLITE DB
    """
    
    from glass.it.shp import shp_to_shp
    
    return shp_to_shp(
        osmXml, osmSQLITE, gapi='ogr', spatialite=True)


def osm_to_gpkg(osm, gpkg):
    """
    Convert OSM file to GeoPackage
    """

    from glass.it.shp import shp_to_shp

    return shp_to_shp(osm, gpkg)


def osm_to_featcls(xmlOsm, output, fileFormat='.shp', useXmlName=None,
                   outepsg=4326):
    """
    OSM to ESRI Shapefile
    """

    import os
    from glass.tbl.filter import sel_by_attr
    from glass.pys.oss  import fprop, del_file
    
    # Convert xml to sqliteDB
    gpkg = osm_to_gpkg(xmlOsm, os.path.join(
        output, fprop(xmlOsm, 'fn') + '.gpkg'))

    # sqliteDB to Feature Class
    TABLES = {'points' : 'pnt', 'lines' : 'lnh',
              'multilinestrings' : 'mlnh', 'multipolygons' : 'poly'}
    
    bname = "" if not useXmlName else fprop(xmlOsm, 'fn') + "_"
    fileFormat = fileFormat if fileFormat[0] == '.' else "." + fileFormat
    oepsg = None if outepsg == 4326 else outepsg
    
    for T in TABLES:
        sel_by_attr(
            gpkg, f"SELECT * FROM {T}",
            os.path.join(output, f"{bname}{TABLES[T]}{fileFormat}"),
            api_gis='ogr', oEPSG=oepsg, iEPSG=4326
        )
    
    # Del temp DB
    del_file(gpkg)

    return output


def getosm_to_featcls(inBoundary, outVector, boundaryEpsg=4326,
                         vectorFormat='.shp'):
    """
    Get OSM Data from the Internet and convert the file to regular vector file
    """

    import os
    from glass.acq.osm import download_by_boundary

    # Download data from the web
    osmData = download_by_boundary(
        inBoundary, os.path.dirname(outVector), 'fresh_osm',
        boundaryEpsg, GetUrl=None
    )

    # Convert data to regular vector file
    return osm_to_featcls(
        osmData, outVector, fileFormat=vectorFormat
    )


"""
Merge OSM
"""

def osm_merge(osm_files, out_osm):
    """
    Multi OSM Files to only one file
    """

    from glass.pys import execmd

    if type(osm_files) != list:
        raise ValueError((
            'osm_files must be a list with path to several '
            'OSM Files'
        ))
    
    if len(osm_files) == 0:
        raise ValueError((
            'osm_files must be a non empty list'
        ))

    rcmd = execmd("osmium merge {} -o {}".format(
        " ".join(osm_files), out_osm
    ))

    return out_osm

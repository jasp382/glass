

def fext_to_geof(inF, outF, ocellsize=10, epsg=None, oepsg=None):
    """
    Extent of a File to Raster or Shapefile
    """
    
    from glass.wt.shp   import coords_to_boundshp
    from glass.wt.rst   import ext_to_rst
    from glass.prop.ext import get_ext
    from glass.prop.df  import is_shp, is_rst
    from glass.prop.prj import get_epsg
    
    # Get extent
    left, right, bottom, top = get_ext(inF)
    
    # Get EPSG of inF
    epsg = get_epsg(inF) if not epsg else epsg
    
    # Export Boundary
    isrst, isshp = is_rst(outF), is_shp(outF)
    
    if isrst and not isshp:
        of = ext_to_rst(
            (left, top), (right, bottom), outF,
            cellsize=ocellsize, epsg=epsg, outEpsg=oepsg,
            invalidResultAsNull=None
        )
    elif not isrst and isshp:
        of = coords_to_boundshp(
            (left, top), (right, bottom),
            epsg, outF, outEpsg=oepsg
        )
        
    else:
        raise ValueError(f'{inF} is not recognized as a file with GeoData')
    
    return of


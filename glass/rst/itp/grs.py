"""
Raster tools - GRASS GIS

GRASS GIS Interpolation Tools
"""


def vidw(inShp, col, outdem, nrPnt=None, _power=None):
    """
    v.surf.idw - Provides surface interpolation from vector point data by
    Inverse Distance Squared Weighting.
    
    v.surf.idw fills a raster matrix with interpolated values generated from
    a set of irregularly spaced vector data points using numerical approximation
    (weighted averaging) techniques. The interpolated value of a cell is
    determined by values of nearby data points and the distance of the cell
    from those input points. In comparison with other methods, numerical
    approximation allows representation of more complex surfaces (particularly
    those with anomalous features), restricts the spatial influence of any
    errors, and generates the interpolated surface from the data points.
    
    Values to interpolate are read from column option. If this option is not
    given than the program uses categories as values to interpolate or
    z-coordinates if the input vector map is 3D.
    """
    
    from grass.pygrass.modules import Module
    
    nrPnt  = 12 if not nrPnt else nrPnt
    _power = 2.0 if not _power else _power
    
    idw = Module(
        "v.surf.idw", input=inShp, column=col, output=outdem,
        npoints=nrPnt, power=_power,
        run_=False, quiet=True, overwrite=True
    )
    
    idw()

def ridw(inRst, outRst, numberPoints=None):
    """
    r.surf.idw - Provides surface interpolation from raster point data
    by Inverse Distance Squared Weighting.
    
    r.surf.idw fills a grid cell (raster) matrix with interpolated values
    generated from input raster data points. It uses a numerical approximation
    technique based on distance squared weighting of the values of nearest data
    points. The number of nearest data points used to determined the
    interpolated value of a cell can be specified by the user (default:
    12 nearest data points).
    
    If there is a current working mask, it applies to the output raster map.
    Only those cells falling within the mask will be assigned interpolated
    values. The search procedure for the selection of nearest neighboring
    points will consider all input data, without regard to the mask.
    The -e flag is the error analysis option that interpolates values
    only for those cells of the input raster map which have non-zero
    values and outputs the difference (see NOTES below).
    
    The npoints parameter defines the number of nearest data points used to
    determine the interpolated value of an output raster cell.
    """
    
    from grass.pygrass.modules import Module
    
    numberPoints = 12 if not numberPoints else numberPoints
    
    idw = Module(
        'r.surf.idw', input=inRst, output=outRst, npoints=numberPoints,
        run_=False, quiet=True, overwrite=True
    )
    
    idw()


def bspline(inPnt, attrCol, rstOutput, lyrN=1, asCMD=None, mway="bilinear"):
    """
    v.surf.bspline performs a bilinear/bicubic spline interpolation
    with Tykhonov regularization. The input is a 2D or 3D vector points
    map. Values to interpolate can be the z values of 3D points or the values
    in a user-specified attribute column in a 2D or 3D vector map.
    Output can be a raster (raster_output) or vector (output) map.
    Optionally, a "sparse point" vector map can be input which indicates
    the location of output vector points.
    """
    
    # Methods Available: bilinear; bicubic
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        t = Module(
            "v.surf.bspline", input=inPnt, layer=lyrN, column=attrCol,
            raster_output=rstOutput, method=mway, overwrite=True,
            quiet=True, run_=False
        )
        
        t()
    
    else:
        from glass.pys import execmd
        
        tcmd = (
            f"v.surf.bspline input={inPnt} layer={lyrN} column={attrCol} "
            f"raster_output={rstOutput} method={mway} "
            "--overwrite --quiet"
        )
        
        rcmd = execmd(tcmd)
    
    return rstOutput

def surfrst(inPnt, attrCol, output, lyrN=1, ascmd=None):
    """
    v.surf.rst - Performs surface interpolation from vector points map by
    splines. Spatial approximation and topographic analysis from given point or
    isoline data in vector format to floating point raster format using
    regularized spline with tension.
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        t = Module(
            "v.surf.rst", input=inPnt, layer=lyrN, zcolumn=attrCol,
            elevation=output, overwrite=True, quiet=True, run_=False
        )
        
        t()
    
    else:
        from glass.pys import execmd

        tcmd = (
            f"v.surf.rst input={inPnt} layer={lyrN} zcolumn={attrCol} "
            f"elevation={output} --overwrite --quiet"
        )
        
        rcmd = execmd(tcmd)
    
    return output


def surfcontour(inContour, outDEM, ascmd=None):
    """
    r.surf.contour - Generates surface raster map from rasterized contours.
    
    r.surf.contour creates a raster elevation map from a rasterized contour map.
    Elevation values are determined using procedures similar to a manual methods.
    To determine the elevation of a point on a contour map, an individual
    might interpolate its value from those of the two nearest contour lines
    (uphill and downhill).
    
    r.surf.contour works in a similar way. Initially, a vector map of the
    contour lines is made with the elevation of each line as an attribute.
    When the program v.to.rast is run on the vector map, continuous "lines"
    of rasters containing the contour line values will be the input for
    r.surf.contour. For each cell in the input map, either the cell is a
    contour line cell (which is given that value), or a flood fill is generated
    from that spot until the fill comes to two unique values. So the
    r.surf.contour algorithm linearly interpolates between contour lines.
    The flood fill is not allowed to cross over the rasterized contour lines,
    thus ensuring that an uphill and downhill contour value will be the two
    values chosen. r.surf.contour interpolates from the uphill and downhill
    values by the true distance.
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        t = Module(
            "r.surf.contour", input=inContour, output=outDEM,
            run_=False, quiet=True, overwrite=True
        )
        
        t()
    
    else:
        from glass.pys import execmd
        
        tcmd = "r.surf.contour input={} output={}".format(inContour, outDEM)
        
        rcmd = execmd(tcmd)
    
    return outDEM


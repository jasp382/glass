"""
Tools for sampling
"""

import os

from glass.pys import execmd

"""
Fishnets
"""

def grass_fishnet(fish_shp, ascmd=None):
    """
    Create fishnet using GRASS GIS tool
    """

    if not ascmd:
        from grass.pygrass.modules import Module

        m = Module(
            "v.mkgrid", map=fish_shp, position='region',
            overwrite=True, run_=False, quiet=True
        )

        m()
    
    else:
        rcmd = execmd((
            f'v.mkgrid map={fish_shp} position=region '
            '--overwrite --quiet'
        ))

    return fish_shp


def create_fishnet(boundary, x, y, shpfishnet=None,
    xy_row_col=None, srs=None, outepsg=None):
    """
    Create a Fishnet
    """
    
    from glass.prop.ext import get_ext
    from glass.prop.prj import get_epsg
    from glass.smp.obj  import fishnet

    # Check Path
    if shpfishnet:
        if not os.path.exists(os.path.dirname(shpfishnet)):
            raise ValueError('The path for the output doesn\'t exist')
    
    # Get boundary extent
    xmin, xmax, ymin, ymax = get_ext(boundary, outEpsg=outepsg)
    # Get SRS
    epsg = int(outepsg) if outepsg else get_epsg(
        boundary) if not srs else int(srs)
    
    return fishnet(
        (xmin, ymax), (xmax, ymin),
        x, y, xy_row_col=xy_row_col, epsg=epsg, outfishnet=shpfishnet
    )


def nfishnet_fm_rst(rst, max_row, max_col, out_fld):
    """
    Create N fishnets for the extent of one raster file
    the number of fishnets (N) will be determined by the extent of the raster
    and values max_row/max_col

    Fishnet cellsize will be the same as the raster
    """

    from osgeo          import gdal
    from glass.prop.img import rst_epsg
    from glass.smp.obj  import fishnet

    # Open Raster
    img = gdal.Open(rst)

    # Get EPSG
    epsg = rst_epsg(img)

    # Get Cellsize
    tl_x, cs_x, xr, tl_y, yr, cs_y = img.GetGeoTransform()

    # Get N cols and Rows
    numimg = img.ReadAsArray()
    nrows = numimg.shape[0]
    ncols = numimg.shape[1]

    # Get raster max_x and min_y
    rst_max_x = tl_x + (ncols * cs_x)
    rst_min_y = tl_y + (nrows * cs_y)

    # Fishnet N
    fnrows = int(nrows / max_row)
    fnrows = fnrows if fnrows == nrows / max_row else fnrows + 1
    fncols = int(ncols / max_col)
    fncols = fncols if fncols == ncols / max_col else fncols + 1

    fi = 1
    fishp = []
    for i in range(fnrows):
        # TopLeft Y
        tly = tl_y + ((max_row * cs_y) * i)

        # BottomRight Y
        bry = tly + (cs_y * max_row)
        # If fishnet min y is lesser than raster min_y
        # Use raster min_y

        if bry < rst_min_y:
            bry = rst_min_y
        
        for e in range(fncols):
            # TopLeft X 
            tlx = tl_x + ((max_col * cs_x) * e)

            # BottomRight X
            brx = tlx + (cs_x * max_col)

            # If fishnet max x is greater than raster max_x
            # Use raster max_x
            if brx > rst_max_x:
                brx = rst_max_x
            
            # Create fishnet file
            fshp = fishnet(
                (tlx, tly), (brx, bry),
                cs_x, abs(cs_y),
                os.path.join(out_fld, f'fishnet_{str(fi)}.shp'),
                epsg=epsg
            )

            fishp.append(fshp)

            fi += 1

    return fishp


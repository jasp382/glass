"""
Merge, combine and mosaic
"""

def rsts_to_mosaic(inRasterS, o, api="grass", fformat='.tif', method=None):
    """
    Create Mosaic of Raster
    """

    if api == 'pygrass':
        """
        The GRASS program r.patch allows the user to build a new raster map the size
        and resolution of the current region by assigning known data values from
        input raster maps to the cells in this region. This is done by filling in
        "no data" cells, those that do not yet contain data, contain NULL data, or,
        optionally contain 0 data, with the data from the first input map.
        Once this is done the remaining holes are filled in by the next input map,
        and so on. This program is useful for making a composite raster map layer
        from two or more adjacent map layers, for filling in "holes" in a raster map
        layer's data (e.g., in digital elevation data), or for updating an older map
        layer with more recent data. The current geographic region definition and
        mask settings are respected.
        The first name listed in the string input=name,name,name, ... is the name of
        the first map whose data values will be used to fill in "no data" cells in
        the current region. The second through last input name maps will be used,
        in order, to supply data values for for the remaining "no data" cells.
        """

        from grass.pygrass.modules import Module
    
        m = Module(
            "r.patch", input=inRasterS, output=o,
            overwrite=True, run_=False, quiet=True
        )
    
        m()
    
    elif api == 'grass':
        from glass.pys import execmd
        
        rcmd = execmd((
            f"r.patch input={','.join(inRasterS)} output={o} "
            "--overwrite --quiet"
        ))
    
    elif api == 'rasterio':
        import rasterio
        from rasterio.merge import merge
        from glass.prop.df  import drv_name
        from glass.prop.prj import get_epsg, epsg_to_wkt

        if type(inRasterS) != list:
            from glass.pys.oss import lst_ff

            rsts = lst_ff(inRasterS, file_format=fformat)
        else: rsts = inRasterS

        methods = ['first', 'last', 'min', 'max']

        method = 'first' if not method or \
            method not in methods else method

        srcs = [rasterio.open(r) for r in rsts]

        mosaic, out_trans = merge(srcs, method=method)

        out_meta = srcs[0].meta.copy()

        out_meta.update({
            "driver"    : drv_name(o),
            "height"    : mosaic.shape[1],
            "width"     : mosaic.shape[2],
            "transform" : out_trans,
            "count"     : 1,
            "crs"       : epsg_to_wkt(get_epsg(rsts[0])),
            "compress"  : 'lzw'
        })

        with rasterio.open(o, "w", **out_meta) as dest:
            dest.write(mosaic)
    
    else:
        raise ValueError(f'api {api} is not available')
    
    return o


def rseries(lst, out, meth, as_cmd=None):
    """
    r.series - Makes each output cell value a function of the values
    assigned to the corresponding cells in the input raster map layers.

    Method Options:
    average, count, median, mode, minimum, min_raster, maximum,
    max_raster, stddev, range, sum, variance, diversity,
    slope, offset, detcoeff, tvalue, quart1, quart3, perc90,
    quantile, skewness, kurtosis
    """

    if type(lst) != list:
        raise ValueError("lst must be a list of rasters")

    if not as_cmd:
        from grass.pygrass.modules import Module
    
        serie = Module(
            'r.series', input=lst, output=out, method=meth,
            overwrite=True, quiet=True, run_=False
        )
    
        serie()
    
    else:
        from glass.pys import execmd

        ilst = ",".join(lst)

        rcmd = execmd((
            f"r.series input={ilst} output={out} "
            f"method={meth} "
            "--overwrite --quiet"
        ))
    
    return out


def fullgrass_rseries(ifolder, refrst, method, orst):
    """
    R. Series using grass
    """

    import os

    from glass.wenv.grs import run_grass
    from glass.pys.tm import now_as_str
    from glass.pys.oss import lst_ff, fprop

    loc = now_as_str()

    gbase = run_grass(ifolder, location=loc, srs=refrst)

    import grass.script.setup as gsetup

    gsetup.init(gbase, ifolder, loc, "PERMANENT")

    from glass.it.rst import rst_to_grs, grs_to_rst

    rsts = [rst_to_grs(
        r, fprop(r, 'fn')
    ) for r in lst_ff(ifolder, file_format='.tif')]

    prst = rseries(rsts, fprop(orst, 'fn'), method, as_cmd=True)

    grs_to_rst(prst, orst)

    return orst


def bnds_to_mosaic(bands, outdata, ref_raster, loc=None):
    """
    Satellite image To mosaic
    
    bands = {
        'bnd_2' : [path_to_file, path_to_file],
        'bnd_3' : [path_to_file, path_to_file],
        'bnd_4' : [path_to_file, path_to_file],
    }
    """
    
    """
    Start GRASS GIS Session
    """
    
    import os
    from glass.pys.oss  import fprop
    from glass.prop.prj import rst_epsg
    from glass.wenv.grs import run_grass

    # Get EPSG from refRaster
    epsg = rst_epsg(ref_raster, returnIsProj=None)
    
    LOC = loc if loc else 'gr_loc'
    grass_base = run_grass(
        outdata, grassBIN='grass78',
        location=LOC, srs=epsg
    )
    
    import grass.script.setup as gsetup
    
    gsetup.init(grass_base, outdata, LOC, 'PERMANENT')
    
    # ************************************************************************ #
    # GRASS MODULES #
    # ************************************************************************ #
    from glass.it.rst import rst_to_grs, grs_to_rst
    from glass.wenv.grs import rst_to_region
    # ************************************************************************ #
    # SET GRASS GIS LOCATION EXTENT #
    # ************************************************************************ #
    extRst = rst_to_grs(ref_raster, 'extent_raster')
    rst_to_region(extRst)
    # ************************************************************************ #
    # SEND DATA TO GRASS GIS #
    # ************************************************************************ #
    grs_bnds = {}
    
    for bnd in bands:
        l= []
        for b in bands[bnd]:
            bb = rst_to_grs(b, fprop(b, 'fn'))
            l.append(bb)
        
        grs_bnds[bnd] = l
    # ************************************************************************ #
    # PATCH bands and export #
    # ************************************************************************ #
    for bnd in grs_bnds:
        mosaic_band = rseries(grs_bnds[bnd], bnd, 'maximum')
        
        grs_bnds[bnd] = grs_to_rst(mosaic_band, os.path.join(
            outdata, mosaic_band + '.tif'
        ), as_cmd=True)
    
    return grs_bnds


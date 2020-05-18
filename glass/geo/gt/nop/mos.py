"""
Merge, combine and mosaic
"""

def rsts_to_mosaic(inRasterS, o, api="grass", fformat='.tif'):
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
        from glass.pyt import execmd
        
        rcmd = execmd("r.patch input={} output={} --overwrite --quiet".format(
            ",".join(inRasterS), o
        ))
    
    elif api == 'rasterio':
        import os;           import rasterio
        from rasterio.merge  import merge
        from glass.geo.gt.prop.ff import drv_name

        if type(inRasterS) != list:
            from glass.pyt.oss import lst_ff

            rsts = lst_ff(inRasterS, file_format=fformat)
        else: rsts = inRasterS

        srcs = [rasterio.open(r) for r in rsts]

        mosaic, out_trans = merge(srcs)

        out_meta = srcs[0].meta.copy()

        out_meta.update({
            "driver"    : drv_name(o),
            "height"    : mosaic.shape[1],
            "width"     : mosaic.shape[2],
            "transform" : out_trans,
            "compress"  : 'lzw'
        })

        with rasterio.open(o, "w", **out_meta) as dest:
            dest.write(mosaic)
    
    else:
        raise ValueError('api {} is not available'.format(api))
    
    return o


def rseries(lst, out, meth):
    
    from grass.pygrass.modules import Module
    
    serie = Module(
        'r.series', input=lst, output=out, method=meth,
        overwrite=True, quiet=True, run_=False
    )
    
    serie()
    
    return out


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
    from glass.pyt.oss         import fprop
    from glass.geo.gt.prop.prj import get_rst_epsg
    from glass.geo.wenv.grs    import run_grass

    # Get EPSG from refRaster
    epsg = get_rst_epsg(ref_raster, returnIsProj=None)
    
    LOC = loc if loc else 'gr_loc'
    grass_base = run_grass(
        outdata, grassBIN='grass78',
        location=LOC, srs=epsg
    )
    
    import grass.script as grass
    import grass.script.setup as gsetup
    
    gsetup.init(grass_base, outdata, LOC, 'PERMANENT')
    
    # ************************************************************************ #
    # GRASS MODULES #
    # ************************************************************************ #
    from glass.geo.gt.torst import rst_to_grs, grs_to_rst
    from glass.geo.wenv.grs import rst_to_region
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


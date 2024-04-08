from glass.pys import execmd


def rsts_to_mosaic(inRasterS, o, api="grass", fformat='.tif', method=None, _nprocs=1):
    """
    Create Mosaic of Raster
    """

    _nprocs = _nprocs if _nprocs else 1

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
            nprocs=_nprocs,
            overwrite=True, run_=False, quiet=True
        )
    
        m()
    
    elif api == 'grass':
        
        rcmd = execmd((
            f"r.patch input={','.join(inRasterS)} output={o} "
            f"nprocs={str(_nprocs)} --overwrite --quiet"
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


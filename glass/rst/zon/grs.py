def grs_rst_stats_by_feat(vec, rst, ncol, method, as_cmd=True):
    """
    DESCRIPTION
    v.rast.stats calculates basic univariate statistics from a raster map only
    for the parts covered by the specified vector map. The vector map will be
    rasterized according to the raster map resolution. Then univariate statistics
    are calculated per vector category (cat) from the raster map and the results
    uploaded to the vector map attribute table. A new column is generated in the
    attribute table for each statistic requested in method (if not already present).
    
    The univariate statistics include the number of raster cells counted, the
    number of raster NULL cells counted, minimum and maximum cell values,
    range, average, standard deviation, variance, coefficient of variation,
    sum, first quartile, median, third quartile, and percentile.

    method options:
    number, null_cells, minimum, maximum, range, average, stddev,
    variance, coeff_var, sum, first_quartile, median, third_quartile, percentile
    """

    from glass.pys import obj_to_lst

    ncol   = obj_to_lst(ncol)
    method = obj_to_lst(method)

    if as_cmd:
        from glass.pys import execmd

        rcmd = execmd((
            f"v.rast.stats map={vec} raster={rst} "
            f"column_prefix={','.join(ncol)} "
            f" method={','.join(method)} -c --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module

        m = Module(
            'v.rst.stats', map=vec, raster=rst, column_prefix=ncol,
            method=method, flags='c', quiet=True, run_=False
        )

        m()

    return vec


def rstatszonal(base, cover, method, output, api='grass', grids=None):
    """
    Zonal Raster Statistics (overlay input as Raster)

    method :: count, average, sum, etc. check r.stats.zonal doc
    base :: the grass raster which has the various regions mask (e.g. r.clump)
    cover :: the grass raster which contains the values used in statistics

    """

    if api == 'grass':
        from glass.pys import execmd

        rcmd = execmd((
            f"r.stats.zonal base={base} cover={cover} method={method} "
            "output={output} --overwrite --quiet"
        ))

    else:
        raise ValueError(f"{api} is not available!")

    return output


"""
Zonal GRASS GIS tools
"""

from glass.pys import execmd


def region_group(in_rst, out_rst, diagonal=True):
    """
    Equivalent to ArcGIS Region Group Tool
    
    r.clump finds all areas of contiguous cell category values in the input
    raster map. NULL values in the input are ignored. It assigns a unique
    category value to each such area ("clump") in the resulting output raster
    map.
    
    Category distinctions in the input raster map are preserved. This means
    that if distinct category values are adjacent, they will NOT be clumped
    together. The user can run r.reclass prior to r.clump to recategorize cells
    and reassign cell category values.
    """
    
    from grass.pygrass.modules import Module
    
    if diagonal:
        m = Module(
            'r.clump', input=in_rst, output=out_rst, flags='d',
            overwrite=True, quiet=True, run_=False
        )
    else:
        m = Module(
            'r.clump', input=in_rst, output=out_rst,
            overwrite=True, quiet=True, run_=False
        )
    
    m()
    
    return out_rst


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


def rstatszonal(base, cover, method, output, api='grass'):
    """
    Zonal Raster Statistics (overlay input as Raster)

    method :: count, average, sum, etc. check r.stats.zonal doc
    base :: the grass raster which has the various regions mask (e.g. r.clump)
    cover :: the grass raster which contains the values used in statistics

    """

    if api == 'grass':
        rcmd = execmd((
            f"r.stats.zonal base={base} cover={cover} "
            f"method={method} output={output} "
            "--overwrite --quiet"
        ))

    else:
        raise ValueError(f"{api} is not available!")

    return output


def reclsbyarea(irst, orst, val, mode='greater',
                method='reclass', i_clump=None, ascmd=True):
    """
    r.reclass.area - Reclasses a raster map greater 
    or less than user specified area size (in hectares).

    If the -c flag is used, r.reclass.area will skip the
    creation of a clumped raster and assume that the input
    raster is already clumped.

    
    input=name [required]
        Name of input raster map
    output=name [required]
        Name for output raster map
    value=float [required]
        Value option that sets the area size limit (in hectares)
    mode=string [required]
        Lesser or greater than specified value
        Options: lesser, greater
    method=string
        Method used for reclassification
        Options: reclass, rmarea
        Default: reclass 
    """

    mode = 'greater' if mode == 'greater' else 'lesser'

    if ascmd:
        flags = ' -c' if i_clump else ''
        rcmd = execmd((
            f'r.reclass.area input={irst} '
            f'output={orst} mode={mode} value={str(val)} '
            f'method={method}{flags} --overwrite --quiet'
        ))
    
    else:
        from grass.pygrass.modules import Module

        m = Module(
            'r.reclass.area', input=irst,
            output=orst, mode=mode, value=val,
            method=method, overwrite=True, quiet=True,
            run_=False,
            flags='c' if i_clump else None
        )

        m()
    
    return orst


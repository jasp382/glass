"""
Grouping and Zonal geometries
"""

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


def zonal_geometry(in_rst, out_rst, work):
    """
    Equivalent to ArcGIS Zonal Geometry Tool
    
    r.object.geometry calculates form statistics of raster objects in the input
    map and writes it to the output text file (or standard output if no output
    filename or '-' is given), with fields separated by the chosen separator.
    Objects are defined as clumps of adjacent cells with the same category
    value (e.g. output of r.clump or i.segment).
    """
    
    import os
    import codecs
    from grass.pygrass.modules import Module
    from glass.rst.rcls import rcls_rst
    
    txt_file = os.path.join(work, 'report.txt')
    r_geometry = Module(
        'r.object.geometry', input=in_rst, output=txt_file, flags='m',
        separator=',', overwrite=True, quiet=True, run_=False
    )
    r_geometry()
    
    recls_rules = os.path.join(work, 'reclass.txt')
    opened_rules = open(txt_file, 'r')
    with codecs.open(recls_rules, 'w', encoding='utf-8') as f:
        c = 0
        for line in opened_rules.readlines():
            if not c:
                c+=1
            else:
                cols = line.split(',')
                f.write('{}  = {} \n'.format(
                    cols[0], str(int(float(cols[1])))
                ))
        f.close()
        opened_rules.close()
    
    rcls_rst(in_rst, recls_rules, out_rst, api='pygrass')
    
    return out_rst


def rst_stats_by_feat(vec, rst, ncol, method, as_cmd=True):
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

    ncol= obj_to_lst(ncol)
    method = obj_to_lst(method)

    if as_cmd:
        from glass.pys import execmd

        rcmd = execmd((
            "v.rast.stats map={} raster={} column_prefix={} "
            " method={} -c --quiet"
        ).format(
            vec, rst, ",".join(ncol), ",".join(method)
        ))
    
    else:
        from grass.pygrass.modules import Module

        m = Module(
            'v.rst.stats', map=vec, raster=rst, column_prefix=ncol,
            method=method, flags='c', quiet=True, run_=False
        )

        m()

    return vec


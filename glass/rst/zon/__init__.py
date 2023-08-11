"""
Grouping and Zonal geometries
"""

import os




def zonal_geometry(in_rst, out_rst, work):
    """
    Equivalent to ArcGIS Zonal Geometry Tool
    
    r.object.geometry calculates form statistics of raster objects in the input
    map and writes it to the output text file (or standard output if no output
    filename or '-' is given), with fields separated by the chosen separator.
    Objects are defined as clumps of adjacent cells with the same category
    value (e.g. output of r.clump or i.segment).
    """
    
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
                f.write(f'{cols[0]}  = {str(int(float(cols[1])))} \n')
        f.close()
        opened_rules.close()
    
    rcls_rst(in_rst, recls_rules, out_rst, api='pygrass')
    
    return out_rst


def rst_stats_eachfeat(vec, rst, col, meth, outvec):
    """
    DESCRIPTION
    calculates basic univariate statistics from a raster map only
    for the parts covered by the specified vector map. The vector map will be
    rasterized according to the raster map resolution. Then univariate statistics
    are calculated per vector category (cat) from the raster map and the results
    uploaded to the vector map attribute table. A new column is generated in the
    attribute table for each statistic requested in method (if not already present).
    """

    from glass.pys.oss  import fprop
    from glass.wenv.grs import run_grass
    from glass.tbl.col  import rn_cols

    # Create GRASS GIS Session
    gw = os.path.dirname(vec)
    vname = fprop(vec, 'fn')
    lc = 'l_' + vname

    gbase = run_grass(gw, location=lc, srs=rst)

    import grass.script.setup as gsetup

    gsetup.init(gbase, gw, lc, 'PERMANENT')

    from glass.it.shp import shp_to_grs, grs_to_shp
    from glass.it.rst import rst_to_grs
    from glass.rst.zon.grs import grs_rst_stats_by_feat

    # Import data
    gvec = shp_to_grs(vec, vname)
    grst = rst_to_grs(rst, fprop(rst, 'fn'))

    nvec = grs_rst_stats_by_feat(gvec, grst, col, meth, as_cmd=True)

    rn_cols(nvec, {f"{col}_{meth}" : col}, api="grass")

    # Export data
    res = grs_to_shp(nvec, outvec, 'area')

    return outvec


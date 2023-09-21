"""
Find Water Bodies from OSM
"""

import os


def water_fm_s2_osm(waterlines: str, green:str, nir_swir:str, waterpoly:str):
    """
    Find water bodies from OSM Lines and Sentinel-2 data
    """

    from glass.pys.oss import mkdir, fprop
    from glass.pys.tm import now_as_str
    from glass.wenv.grs import run_grass

    # Setup grass GIS session
    ws, loc = mkdir(os.path.join(
        os.path.dirname(waterpoly),
        fprop(waterpoly, 'fn')
    ), overwrite=True), now_as_str()
    
    gb = run_grass(ws, location=loc, srs=green)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    from glass.it.shp        import shp_to_grs, grs_to_shp
    from glass.it.rst        import rst_to_grs
    from glass.rst.alg       import grsrstcalc
    from glass.rst.zon.grs   import region_group, reclsbyarea
    from glass.dtt.rst.toshp import rst_to_polyg
    from glass.gp.ovl.grs    import grs_select

    # Data to GRASS GIS
    lines = shp_to_grs(waterlines)
    g, ns = rst_to_grs(green), rst_to_grs(nir_swir)

    # Calculate NDWI
    ndwi = grsrstcalc(
        f"({g} - {ns}) / ({g} + float({ns}))",
        'ndwi'
    )

    # Get Water Bodies
    wbodies = grsrstcalc(
        f"if({ndwi} > 0.5, 1, null())",
        'wbodies'
    )

    # Group cells in regions
    wbodiesgrp = region_group(wbodies, 'wgroups')

    # Remove regions with area < 0.5 ha
    wbodiesreg = reclsbyarea(
        wbodiesgrp, 'rel_water', 0.5,
        mode='greater', method="reclass",
        i_clump=True, ascmd=True
    )

    # Water regions to vetorial
    wshp = rst_to_polyg(
        wbodiesreg, fprop(waterpoly, 'fn'),
        api='grass'
    )

    ires = grs_select(
        wshp, lines, 'wbodies_intersect',
        'overlap'
    )

    crosses = grs_select(
        wshp, lines, 'wbodies_crosses',
        'crosses'
    )

    contain = grs_select(
        wshp, lines, 'wbodies_contains',
        'contains'
    )

    # Export result
    grs_to_shp(ires, waterpoly, 'area')

    grs_to_shp(crosses, os.path.join(
        os.path.dirname(waterpoly),
        crosses + '.shp'
    ), 'area')

    grs_to_shp(contain, os.path.join(
        os.path.dirname(waterpoly),
        contain + '.shp'
    ), 'area')

    return waterpoly


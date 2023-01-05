"""
Network Analysis
"""

import os

from glass.pys.oss  import fprop
from glass.wenv.grs import run_grass


def run_close_facility(rdv, incidents, facilities, kph, oneway, output):
    """
    Closest facility full procedure using GRASS GIS
    """

    # Start GRASS GIS Session
    ws = os.path.dirname(output)
    loc = f"loc_{fprop(output, 'fn')}"

    gb = run_grass(ws, location=loc, srs=rdv)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    from glass.it.shp          import shp_to_grs, grs_to_shp
    from glass.mob.grstbx.vnet import pnts_to_net
    from glass.mob.grstbx.anls import closest_facility
    from glass.tbl             import category
    from glass.tbl.grs         import add_table, cols_calc
    from glass.dtr.cp.grs       import copy_insame_vector
    from glass.tbl.attr        import geomattr_to_db

    # Add data to GRASS GIS
    rdvgrs = shp_to_grs(rdv, fprop(rdv, 'fn'))

    igrs = shp_to_grs(incidents, fprop(incidents, 'fn'))
    fgrs = shp_to_grs(facilities, fprop(facilities, 'fn'))

    # Add incidents and facilities to the network
    i_rdv = pnts_to_net(rdvgrs, igrs, 'rdv_incidents', pntlyr=2, ascmd=True)

    if_rdv = pnts_to_net(i_rdv, fgrs, 'rdv_incfac', pntlyr=3, ascmd=True)

    # Sanitize Network Table and Cost Columns
    cat_rdv = category(
        if_rdv, 'rdv_incfac_ncat', "add",
        LyrN="4", geomType="line", asCMD=True
    )
    
    add_table(cat_rdv, (
        "cat integer,kph integer,length double precision,"
        "ft_minutes double precision,"
        "tf_minutes double precision,oneway text"
    ), lyrN=4, asCMD=True)

    copy_insame_vector(cat_rdv, "kph", kph, 4, geomType="line", asCMD=True)
    copy_insame_vector(cat_rdv, "oneway",  oneway, 4, geomType="line", asCMD=True)

    geomattr_to_db(
        cat_rdv, "length", "length", "line",
        createCol=False, unit="meters", lyrN=4, ascmd=True
    )
    
    cols_calc(cat_rdv, "kph", "5",  "kph IS NULL", lyrN=4, ascmd=True)
    cols_calc(cat_rdv, "kph", "5", "oneway = 'N'", lyrN=4, ascmd=True)
    cols_calc(
        cat_rdv, "ft_minutes",
        "(length * 60) / (kph * 1000.0)",
        "ft_minutes IS NULL", lyrN=4, ascmd=True
    ); cols_calc(
        cat_rdv, "tf_minutes",
        "(length * 60) / (kph * 1000.0)",
        "tf_minutes IS NULL", lyrN=4, ascmd=True
    )
    
    # Exagerate Oneway's
    cols_calc(
        cat_rdv, "ft_minutes", "1000", "oneway = 'TF'",
        lyrN=4, ascmd=True
    )
    cols_calc(
        cat_rdv, "tf_minutes", "1000", "oneway = 'FT'",
        lyrN=4, ascmd=True
    )
    
    #grs_to_shp(if_rdv, os.path.join(ws, loc, f"{if_rdv}_1.shp"), "line", lyrn=1)
    #grs_to_shp(if_rdv, os.path.join(ws, loc, f"{if_rdv}_2.shp"), "point", lyrn=2)
    #grs_to_shp(if_rdv, os.path.join(ws, loc, f"{if_rdv}_3.shp"), "point", lyrn=3)

    fnal = closest_facility(
        cat_rdv, 'ft_minutes', 'tf_minutes',
        fprop(output, 'fn'), ascmd=True
    )

    grs_to_shp(fnal, output, "line")
    
    return output


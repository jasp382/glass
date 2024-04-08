"""
GRASS End To End accessibility analysis
"""

import os

from glass.pys.tm import now_as_str
from glass.wenv.grs import grass_session


def con_facilities_to_net(nd, facilities, kph, oneway, felev, telev, new_nd, threshold=5000,
                          ft_minutes="FT_Minutes", tf_minutes="TF_Minutes"):
    """
    Connect facilities to the network

    Impedance == car
    """

    # Start GRASS GIS Session
    ws = os.path.dirname(new_nd)
    loc = now_as_str(utc=True)

    gb = grass_session(ws, loc=loc, srs=nd)

    from glass.it.shp          import shp_to_grs, grs_to_shp
    from glass.mob.grstbx.vnet import pnts_to_net
    from glass.tbl             import category
    from glass.tbl.grs         import add_table, cols_calc
    from glass.dtt.cp.grs      import copy_insame_vector
    from glass.tbl.attr        import geomattr_to_db

    # Add data to GRASS GIS
    rdvgrs = shp_to_grs(nd)

    fgrs = shp_to_grs(facilities)

    f_rdv = pnts_to_net(rdvgrs, fgrs, 'rdv_fac', __threshold=threshold,ascmd=True)

    # Sanitize Network Table and Cost Columns
    cat_rdv = category(
        f_rdv, 'rdv_fac_ncat', "add",
        LyrN="3", geomType="line", asCMD=True
    )
    
    add_table(cat_rdv, (
        f"cat integer,{kph} integer,length double precision,"
        f"{ft_minutes} double precision,"
        f"{tf_minutes} double precision,{oneway} text,"
        f"{felev} integer,{telev} integer"
    ), lyrN=3, asCMD=True)

    copies = {
        "kph"    : kph,
        "oneway" : oneway,
        "f_elev" : felev,
        "t_elev" : telev
    }

    for c in copies:
        copy_insame_vector(
            cat_rdv, copies[c], copies[c], 3, geomType="line", asCMD=True,
            query_layer=1
        )

    geomattr_to_db(
        cat_rdv, "length", "length", "line",
        createCol=False, unit="meters", lyrN=3, ascmd=True
    )

    place_null = {
        "kph"    : "5",
        "oneway" : "B",
        "f_elev" : "0",
        "t_elev" : "0"
    }

    for f in place_null:
        cols_calc(
            cat_rdv, copies[f], place_null[f],  f"{copies[f]} IS NULL",
            lyrN=3, ascmd=None, qcol=False
        )
        
    #cols_calc(cat_rdv, "kph", "5", "oneway = 'N'", lyrN=3, ascmd=None)
    cols_calc(
        cat_rdv, ft_minutes,
        f"(length * 60) / ({kph} * 1000.0)",
        f"{ft_minutes} IS NULL", lyrN=3, ascmd=None, qcol=True
    )
    cols_calc(
        cat_rdv, tf_minutes,
        f"(length * 60) / ({kph} * 1000.0)",
        f"{tf_minutes} IS NULL", lyrN=3, ascmd=None, qcol=True
    )

    # Export result
    grs_to_shp(cat_rdv, new_nd, "line", lyrn=3)

    return new_nd



def con_factonet_walk(nd, fac, walkvel, felev, telev, outnd, bname,
                      thrs=5000, ft_minutes="FT_Minutes", tf_minutes="TF_Minutes"):
    """
    Connect facilities to the network

    Impedance == walking
    """

    # Start GRASS GIS Session
    ws = os.path.dirname(outnd)
    loc = now_as_str(utc=True)

    gb = grass_session(ws, loc=loc, srs=nd)

    from glass.it.shp          import shp_to_grs, grs_to_shp
    from glass.mob.grstbx.vnet import pnts_to_net
    from glass.tbl             import category
    from glass.tbl.grs         import add_table, cols_calc
    from glass.dtt.cp.grs      import copy_insame_vector
    from glass.tbl.attr        import geomattr_to_db
    from glass.dtt.mge         import shps_to_shp

    # Merge facilities if necessary
    _fac = shps_to_shp(
        fac, os.path.join(ws, loc, 'merge_fac.shp'),
        api='ogr2ogr'
    ) if type(fac) == list else fac

    # Add data to GRASS GIS
    rdvgrs = shp_to_grs(nd)

    fgrs = shp_to_grs(_fac)

    f_rdv = pnts_to_net(rdvgrs, fgrs, 'rdv_fac', __threshold=thrs,ascmd=True)

    # Sanitize Network Table and Cost Columns
    # for each velocity in walkvel
    copies = {"f_elev" : felev, "t_elev" : telev}
    res = []
    for vel in walkvel:
        cat_rdv = category(
            f_rdv, f'rdv_{str(vel)}kph', "add",
            LyrN="3", geomType="line", asCMD=True
        )

        add_table(cat_rdv, (
            f"cat integer,kph integer,length double precision,"
            f"{ft_minutes} double precision,"
            f"{tf_minutes} double precision,"
            f"{felev} integer,{telev} integer"
        ), lyrN=3, asCMD=True)

        for c in copies:
            copy_insame_vector(
                cat_rdv, copies[c], copies[c], 3, geomType="line", asCMD=True,
                query_layer=1
            )

            cols_calc(
                cat_rdv,  copies[c], 0,  f"{copies[c]} IS NULL",
                lyrN=3, ascmd=None, qcol=False
            )
        
        geomattr_to_db(
            cat_rdv, "length", "length", "line",
            createCol=False, unit="meters", lyrN=3, ascmd=True
        )

        cols_calc(cat_rdv, 'kph', vel, lyrN=3, ascmd=None, qcol=False)
        cols_calc(
            cat_rdv, ft_minutes,
            f"(length * 60) / ({vel} * 1000.0)",
            lyrN=3, ascmd=None, qcol=True
        )
        cols_calc(
            cat_rdv, tf_minutes,
            f"(length * 60) / ({vel} * 1000.0)",
            lyrN=3, ascmd=None, qcol=True
        )

        # Export result
        ri = grs_to_shp(cat_rdv, os.path.join(outnd, f'{bname}_{str(vel)}kph.shp'), "line", lyrn=3)

        res.append(ri)

    return res


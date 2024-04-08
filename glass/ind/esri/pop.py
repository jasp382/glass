"""
Produce indicators using ESRI tools
"""


import os
import pandas as pd
import numpy as np



def pop_by_catinshape(shpe, catcol, units_shp, units_pk, popcol, areacol, resi_shp,
                      resi_fk, otbl, tmpgdb=None):
    """
    Count population in all polygons with
    certain category 
    """

    from glass.esri.gp.ovl    import intersection
    from glass.esri.wenv      import create_geodb
    from glass.pys.tm         import now_as_str
    from glass.pys.oss        import fprop
    from glass.esri.it        import copy_feat
    from glass.esri.rd.shp    import shp_to_lyr
    from glass.esri.tbl.joins import join_table
    from glass.rd.shp         import shp_to_obj
    from glass.wt             import obj_to_tbl

    # Create geodatabase to store temporary files
    tgdb = create_geodb(os.path.dirname(otbl), now_as_str()) if not tmpgdb \
        else tmpgdb

    if resi_shp:
        tlyr = shp_to_lyr(resi_shp, lyrname=f'oresi_{now_as_str()}')
        cp_resi, lyr_resi = copy_feat(tlyr, os.path.join(tgdb, f"{fprop(resi_shp, 'fn')}_{now_as_str()}"))

        # Create feature class with residential areas, total residential area and total population
        lyr_resi = join_table(lyr_resi, units_shp, resi_fk, units_pk, cols=[popcol, areacol])
    
    else:
        lyr_resi = shp_to_lyr(units_shp, lyrname=f"{fprop(units_shp, 'fn')}_{now_as_str()}")

    # Intersection
    i_sa_resi, intlyr = intersection(
        [lyr_resi, shpe],
        os.path.join(tgdb, f'i_sa_resiareas_{now_as_str()}')
    )

    # Open service area shape and get time intervals
    sadf = shp_to_obj(shpe)

    sadf['shpe_area'] = sadf.geometry.area

    tmbreaks = pd.DataFrame(sadf.groupby([catcol]).agg({
        'shpe_area' : 'sum'
    })).reset_index()

    # Open intersection results
    idf = shp_to_obj(i_sa_resi)

    mc = [popcol, areacol, 'geometry', catcol]
    dc = [c for c in idf.columns.values if c not in mc]
    idf.drop(dc, axis=1, inplace=True)

    idf['intarea'] = idf.geometry.area

    idf['interpop'] = (idf['intarea'] * idf[popcol]) / idf[areacol]

    idf_gp = pd.DataFrame(idf.groupby([catcol]).agg({
        'interpop' : 'sum'
    })).reset_index()

    idf_gp['interpop'] = idf_gp['interpop'].round(0).astype(int)

    idf_gp.rename(columns={catcol : 'time_interval'}, inplace=True)

    tmbreaks = tmbreaks.merge(idf_gp, how='left', left_on=catcol, right_on='time_interval')

    tmbreaks.drop('time_interval', axis=1, inplace=True)

    tmbreaks['interpop'] = np.where(
        tmbreaks['interpop'].isna(), 0,
        tmbreaks['interpop']
    )

    tmbreaks.sort_values(by=[catcol], inplace=True)

    obj_to_tbl(tmbreaks, otbl)

    return otbl


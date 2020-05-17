"""
Run shparea_by_mapunitpopulation by each file in folder

Each file will be treated as polygons for each
mapunits groups
"""

import os
import pandas      as pd
from glass.pys.oss import lst_ff
from glass.rd.shp  import shp_to_obj
from glass.ind.pop import shparea_by_mapunitpopulation

if __name__ == '__main__':
    shps_folder = '/home/jasp/mystuff/rms/green_by_conc_v2'

    mapunits = '/home/jasp/mystuff/gigs/conc_rpms.shp'

    mapunits_id = 'idmun'

    mapunit_grp = 'idmun'

    fileformat = '.shp'

    outcol = 'a_verde'
    out_folder = '/home/jasp/mystuff/rms/a_verde_v2'

    # List shapes to use as polygons
    ff = pd.DataFrame(lst_ff(
        shps_folder, file_format=fileformat
    ), columns=['shapefile'])

    # Get Mapunits ID writen in the file name
    tmp_ff = ff.shapefile.str.split("_", n=-1, expand=True)
    ncols = tmp_ff.shape[1]

    ff["refid"] = tmp_ff[ncols-1]
    ff["refid"] = ff.refid.str.replace(fileformat, '')

    # Open mapunits
    munits = shp_to_obj(mapunits)

    # Produce outputs
    for i, row in ff.iterrows():
        funits = munits[munits[mapunit_grp] == row.refid]

        shparea_by_mapunitpopulation(
            row.shapefile, funits, mapunits_id,
            outcol, os.path.join(out_folder, f"{outcol}_{row.refid}.shp"),
            units_pop='pop2011', areacol='area_verde'
        )


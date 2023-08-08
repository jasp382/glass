"""
Run methods in glass.ind.pop using a multiprocessing approach
"""

import os
import multiprocessing as mp
import pandas          as pd

from glass.pys.oss  import cpu_cores, lst_ff
from glass.pd.split import df_split


def thrd_popwithinarea(munits, munits_id, ocol, subunits, sub_id, popcol, munits_fk,
    area_shps, out, oname):
    """
    Run pop_within_area using multiprocessing for each file
    in folders
    """

    from glass.ind.pop import pop_within_area

    # List Map units
    df = pd.DataFrame([[
        str(f.split('.')[0].split('_')[-1]), f
    ] for f in lst_ff(
        munits, file_format='.shp', rfilename=True
    )], columns=['fid', 'mapunits'])

    # List subunits
    _subunits = pd.DataFrame([[
        str(f.split('.')[0].split('_')[-1]), f
    ] for f in lst_ff(
        subunits, file_format='.shp', rfilename=True
    )], columns=['afid', 'subunits'])

    # List interest areas
    iareas = pd.DataFrame([[
        str(f.split('.')[0].split('_')[-1]), f
    ] for f in lst_ff(
        area_shps, file_format='.shp', rfilename=True
    )], columns=['bfid', 'iareas'])

    # Join files references
    dfs = {'afid' : _subunits, 'bfid' : iareas}

    for k in dfs:
        df = df.merge(
            dfs[k], how='left', left_on='fid',
            right_on=k
        )
    
        # Delete rows with NoData Values
        df = df[~df[k].isna()]

    df.drop(list(dfs.keys()), axis=1, inplace=True)

    # Split DFS
    ncpu = cpu_cores()
    _dfs = df_split(df, ncpu)

    # Function to calculate indicator
    def prod_popwarea(_df):
        for i, r in _df.iterrows():
            pop_within_area(
                os.path.join(munits, r.mapunits),
                munits_id, ocol,
                os.path.join(subunits, r.subunits),
                sub_id, popcol, munits_fk,
                os.path.join(area_shps, r.iareas),
                os.path.join(out, f"{oname}_{r.fid}.shp"),
                res_areas=None, res_areas_fk=None
            )
    
    # Run it
    thrds = [mp.Process(
        target=prod_popwarea, name=f'th-{str(i+1)}',
        args=(_dfs[i],)
    ) for i in range(len(_dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()


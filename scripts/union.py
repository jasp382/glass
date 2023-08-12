"""
Union Analysis
"""

def multi_run(ti, df, ofolder):
    if not df.shape[0]: return
    
    loc_name = f'loc_{str(ti)}'
    grsbase = run_grass(ofolder, location=loc_name, srs=srs_epsg)
    
    import grass.script.setup as gsetup

    gsetup.init(grsbase, ofolder, loc_name, 'PERMANENT')
    
    from glass.it.shp     import shp_to_grs, grs_to_shp
    from glass.gp.ovl.grs import grsunion
    
    for idx, row in df.iterrows():
        # Import data into GRASS GIS
        lyr_a = shp_to_grs(row.shp_a, fprop(row.shp_a, 'fn'), asCMD=True)
        lyr_b = shp_to_grs(row.shp_b, fprop(row.shp_b, 'fn'), asCMD=True)
        
        # Run Union
        shpUnion = grsunion(
            lyr_a, lyr_b, f"{lyr_a[:10]}_{lyr_b[:10]}",
            cmd=True
        )
        
        # Export data
        result = grs_to_shp(shpUnion, os.path.join(ofolder, shpUnion + '.shp'), "area")

if __name__ == '__main__':
    import os
    import multiprocessing as mp
    import pandas as pd
    from glass.wenv.grs import run_grass
    from glass.pys.oss  import fprop, cpu_cores
    from glass.pd.split import df_split

    shp_pairs = [
        ['/home/jasp/mystuff/osm2lulc/lulc_lsb_etrs.shp', '/home/jasp/mystuff/osm2lulc/cos_lsb_diss.shp']
    ]

    outshp = '/home/jasp/mystuff/osm2lulc'

    srs_epsg = 3763

    cpu_n = cpu_cores() /2

    df_shp = pd.DataFrame(shp_pairs, columns=['shp_a', 'shp_b'])

    dfs = df_split(df_shp, cpu_n)

    thrds = [mp.Process(
        target=multi_run, name=f'th-{str(i+1)}',
        args=(i+1, dfs[i], outshp)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()


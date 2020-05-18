"""
Union Analysis
"""

def multi_run(ti, df, ofolder):
    loc_name = 'loc_{}'.format(str(ti))
    grsbase = run_grass(ofolder, location=loc_name, srs=srs_epsg)
    
    import grass.script.setup as gsetup
    gsetup.init(grsbase, ofolder, loc_name, 'PERMANENT')
    
    from gasp.gt.toshp.cff import shp_to_grs, grs_to_shp
    from gasp.gt.gop.ovlay import union
    
    for idx, row in df.iterrows():
        # Import data into GRASS GIS
        lyr_a = shp_to_grs(df.shp_a, fprop(df.shp_a, 'fn'), asCMD=True)
        lyr_b = shp_to_grs(df.shp_b, fprop(df.shp_b, 'fn'), asCMD=True)
        
        # Run Union
        shpUnion = union(lyr_a, lyr_b, lyr_a[:10] + '_' + lyr_b[:10], api_gis="grass")
        
        # Export data
        result = grs_to_shp(shpUnion, os.path.join(ofolder, shpUnion + '.shp'), "area")

if __name__ == '__main__':
    import os
    import multiprocessing as mp
    import pandas as pd
    from gasp.gt.wenv.grs  import run_grass
    from gasp.pyt.oss      import fprop, cpu_cores
    from gasp.pyt.df.split import df_split

    shp_pairs = [
        ['/home/jasp/mrgis/cos_union/cos18/shape1.shp', '/home/jasp/mrgis/cos_union/cos95/shape1.shp'],
        ['/home/jasp/mrgis/cos_union/cos18/shape2.shp', '/home/jasp/mrgis/cos_union/cos95/shape2.shp'],
        ['/home/jasp/mrgis/cos_union/cos18/shape3.shp', '/home/jasp/mrgis/cos_union/cos95/shape3.shp'],
        ['/home/jasp/mrgis/cos_union/cos18/shape4.shp', '/home/jasp/mrgis/cos_union/cos95/shape4.shp'],
        ['/home/jasp/mrgis/cos_union/cos18/shape5.shp', '/home/jasp/mrgis/cos_union/cos95/shape5.shp'],
        ['/home/jasp/mrgis/cos_union/cos18/shape6.shp', '/home/jasp/mrgis/cos_union/cos95/shape6.shp'],
        ['/home/jasp/mrgis/cos_union/cos18/shape7.shp', '/home/jasp/mrgis/cos_union/cos95/shape7.shp'],
        ['/home/jasp/mrgis/cos_union/cos18/shape8.shp', '/home/jasp/mrgis/cos_union/cos95/shape8.shp'],
    ]

    outshp = '/home/jasp/mrgis/cos_union/result'

    srs_epsg = 3763

    cpu_n = cpu_cores() /2

    df_shp = pd.DataFrame(shp_pairs, columns=['shp_a', 'shp_b'])

    dfs = df_split(df_shp, cpu_n)

    thrds = [mp.Process(
        target=multi_run, name='th-{}'.format(str(i+1)),
        args=(i+1, dfs[i], outshp)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()


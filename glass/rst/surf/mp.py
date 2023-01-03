"""
Produce multiple rasters using multiprocessing
"""

def rstfld_to_slope(rst_folder, dclv_folder, out_name, perc_folder=None):
    """
    Run slope for each raster in folder
    """

    import os
    import pandas as pd
    import re
    import multiprocessing as mp
    from glass.wenv.grs  import run_grass
    from glass.pys.oss     import cpu_cores, lst_ff
    from glass.pys.oss     import fprop
    from glass.pd.split import df_split

    def run_slope(tid, inrsts, outfolder, oname, percentage):
        """
        Thread function
        """

        iirsts = inrsts.mdt.tolist()

        # Create GRASS GIS Location
        loc_name = f'thread_{str(tid)}'
        gbase = run_grass(
            outfolder, location=loc_name, srs=iirsts[0]
        )

        # Start GRASS GIS Session
        import grass.script as grass
        import grass.script.setup as gsetup
        gsetup.init(gbase, outfolder, loc_name, 'PERMANENT')

        from glass.it.rst   import rst_to_grs, grs_to_rst
        from glass.rst.surf import slope
        from glass.wenv.grs import rst_to_region

        for rst in iirsts:
            # Import data
            mdt = rst_to_grs(rst, fprop(rst, 'fn'))

            # Set region
            rst_to_region(mdt)

            # Get ID in name
            mdt_id = re.search(r'\d+', mdt).group()

            # Get slope
            if percentage:
                slope_perc = slope(
                    mdt, f"pp_{oname}_{mdt_id}",
                    data='percent'
                )
            
            slope_degr = slope(
                mdt, f"{oname}_{mdt_id}", data='degrees'
            )

            # Export
            if percentage:
                grs_to_rst(slope_perc, os.path.join(
                    percentage, slope_degr + '.tif'
                ))
            
            grs_to_rst(slope_degr, os.path.join(
                outfolder, slope_degr + '.tif'
            ))
    
    # List Rasters
    rsts = pd.DataFrame(
        lst_ff(rst_folder, file_format='.tif'),
        columns=['mdt']
    )

    # Split rasters by threads
    ncpu = cpu_cores()

    dfs = df_split(rsts, ncpu)

    # Run slope using multiprocessing
    thrds = [mp.Process(
        target=run_slope, name=f"th_{str(i)}",
        args=(i+1, dfs[i], dclv_folder, out_name, perc_folder)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()

    return dclv_folder


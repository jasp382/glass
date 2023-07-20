"""
Terrain Modelling Tools
"""

import os

def ob_ref_rst(ref, folder, cellsize=None):
    """
    Get Reference Raster
    """

    from glass.prop.df import is_rst, is_shp

    # Check if refRaster is really a Raster
    isRst = is_rst(ref)

    if not isRst:
        if not is_shp(ref):
            raise ValueError((
                'Extent Template File has an invalid file format. '
                'Please give a file with one of the following extensions: '
                'shp, gml, json, kml, tif or img'
            ))
        else:
            # We have a shapefile
            # Convert it to Raster
            from glass.dtt.torst import shp_to_rst

            ref_rst = shp_to_rst(
                ref, None, 10 if not cellsize else cellsize,
                -1, os.path.join(folder, 'ref_raster.tif'), api='gdal'
            )

            return ref_rst
    else:
        return ref


def make_dem(grass_workspace, data, field, output, extent_template,
             method="IDW", cell_size=None, mask=None):
    """
    Create Digital Elevation Model
    
    Methods Available:
    * IDW;
    * BSPLINE;
    * SPLINE;
    * CONTOUR;
    """

    from glass.pys.oss  import fprop
    from glass.wenv.grs import run_grass
    from glass.prop.prj import get_epsg
    
    LOC_NAME = fprop(data, 'fn', forceLower=True)[:5] + "_loc"
    
    # Get EPSG From Raster
    EPSG = get_epsg(extent_template)
    if not EPSG:
        raise ValueError(
            'Cannot get EPSG code of Extent Template File ({})'.format(
                extent_template
            )
        )
    
    # Know if data geometry are points
    if method == 'BSPLINE' or method == 'SPLINE':
        from glass.prop.feat import get_gtype

        data_gtype = get_gtype(data, gisApi='ogr')
    
    # Create GRASS GIS Location
    grass_base = run_grass(grass_workspace, location=LOC_NAME, srs=EPSG)
    
    # Start GRASS GIS Session
    import grass.script.setup as gsetup
    gsetup.init(grass_base, grass_workspace, LOC_NAME, 'PERMANENT')

    # Get Extent Raster
    ref_template = ob_ref_rst(extent_template, os.path.join(
        grass_workspace, LOC_NAME
    ), cellsize=cell_size)
    
    # IMPORT GRASS GIS MODULES #
    from glass.it.rst   import rst_to_grs, grs_to_rst
    from glass.it.shp   import shp_to_grs
    from glass.wenv.grs import rst_to_region
    
    # Configure region
    rst_to_grs(ref_template, 'extent')
    rst_to_region('extent')
    
    # Convert elevation "data" to GRASS Vector
    elv = shp_to_grs(data, 'elevation')
    
    OUTPUT_NAME = fprop(output, 'fn', forceLower=True)
    
    if method == "BSPLINE":
        from glass.rst.itp import bspline

        # Convert to points if necessary
        if data_gtype != 'POINT' and data_gtype != 'MULTIPOINT':
            from glass.dtt.cg import feat_vertex_to_pnt

            elev_pnt = feat_vertex_to_pnt(elv, "elev_pnt", nodes=None)
        else:
            elev_pnt = elv
        
        outRst = bspline(elev_pnt, field, OUTPUT_NAME, mway='bicubic', lyrN=1, asCMD=True)
    
    elif method == "SPLINE":
        from glass.rst.itp import surfrst

        # Convert to points if necessary
        if data_gtype != 'POINT' and data_gtype != 'MULTIPOINT':
            from glass.dtt.cg import feat_vertex_to_pnt
            elev_pnt = feat_vertex_to_pnt(elv, "elev_pnt", nodes=None)
        else:
            elev_pnt = elv
        
        outRst = surfrst(elev_pnt, field, OUTPUT_NAME, lyrN=1, ascmd=True)
    
    elif method == "CONTOUR":
        from glass.dtt.torst import grsshp_to_grsrst as shp_to_rst
        from glass.rst.itp  import surfcontour
        
        # Apply mask if mask
        if mask:
            from glass.it.rst import grs_to_mask, rst_to_grs
            
            rst_mask = rst_to_grs(mask, 'rst_mask', as_cmd=True)
            grs_to_mask(rst_mask)
        
        # Elevation (GRASS Vector) to Raster
        elevRst = shp_to_rst(elv, field, 'rst_elevation')
        
        # Run Interpolator
        outRst = surfcontour(elevRst, OUTPUT_NAME, ascmd=True)
    
    elif method == "IDW":
        from glass.rst.itp  import ridw
        from glass.rst.alg  import grsrstcalc
        from glass.dtt.torst import grsshp_to_grsrst
        
        # Elevation (GRASS Vector) to Raster
        elevRst = grsshp_to_grsrst(elv, field, 'rst_elevation')
        # Multiply cells values by 100 000.0
        grsrstcalc('int(rst_elevation * 100000)', 'rst_elev_int')
        # Run IDW to generate the new DEM
        ridw('rst_elev_int', 'dem_int', numberPoints=15)
        # DEM to Float
        grsrstcalc('dem_int / 100000.0', OUTPUT_NAME)
    
    # Export DEM to a file outside GRASS Workspace
    grs_to_rst(OUTPUT_NAME, output)
    
    return output


def thrd_dem(countours_folder, ref_folder, dem_folder, attr,
    refFormat='.tif', countoursFormat='.shp', demFormat='.tif',
    cellsize=10, masksFolder=None, masksFormat='.tif',
    method="COUNTOURS"):
    """
    Produce DEM using GRASS GIS for all Feature Classes in countours_Folder

    E.g. countours_folder
    1 | data_1.shp
    2 | data_2.shp

    E.g. ref_folder
    1 | lmt_dem_1.tif
    2 | lmt_dem_2.tif

    Filenames must have their id before the extension; '_' must be used to
    separate id from basename.

    Methods Available:
    * IDW;
    * BSPLINE;
    * SPLINE;
    * CONTOUR;
    """

    import os
    import multiprocessing  as mp
    import pandas           as pd
    from glass.pys.oss      import cpu_cores, lst_ff, mkdir
    from glass.pd.split import df_split

    # List Ref Files
    ref = [[
        int(l.split('.')[0].split('_')[-1]), l 
    ] for l in lst_ff(
        ref_folder, file_format=refFormat, rfilename=True
    )]

    # List Countours Files
    countours = [[
        int(c.split('.')[0].split('_')[-1]), c
    ] for c in lst_ff(
        countours_folder, file_format=countoursFormat, rfilename=True
    )]
    
    # List masks if necessary
    masks = None if not masksFolder else [[
        int(m.split('.')[0].split('_')[-1]), m
    ] for m in lst_ff(
        masksFolder, file_format=masksFormat, rfilename=True
    )]

    # Produce DataFrame to better mapping
    df  = pd.DataFrame(ref, columns=['fid', 'ref'])
    jdf = pd.DataFrame(countours, columns=['jfid', 'countours'])
    df  = df.merge(jdf, how='left', left_on='fid', right_on='jfid')
    
    # Add masks meta to df
    if masksFolder:
        mdf = pd.DataFrame(masks, columns=['mfid', 'masks'])
        df = df.merge(mdf, how='left', left_on='fid', right_on='mfid')

    # List DEMs already produced
    dems = lst_ff(dem_folder, file_format=demFormat, rfilename=True)
    
    # Delete rows when dem already exists
    def check_dem_exists(row):
        # Get DEM name
        dem_f = 'dem_{}{}'.format(str(row.fid), demFormat)
        
        row['exists'] = 1 if dem_f in dems else 0
        
        return row
    
    df = df.apply(lambda x: check_dem_exists(x), axis=1)
    df = df[df.exists == 0]

    # Split Dfs
    n_cpu = cpu_cores()
    dfs   = df_split(df, n_cpu) 

    # Function to produce DEM
    def prod_dem(_df):
        for idx, row in _df.iterrows():
            # Get DEM name
            dem_f = 'dem_{}{}'.format(str(row.fid), demFormat)

            # Get GRASS GIS Workspace
            gw = mkdir(os.path.join(
                ref_folder, 'gw_{}'.format(str(row.fid))
            ), overwrite=True)
            
            # Get mask
            msk = None if not masksFolder else None if pd.isna(row.masks)\
                else os.path.join(masksFolder, row.masks)

            # Produce DEM
            make_dem(gw, os.path.join(countours_folder, row.countours),
                attr, os.path.join(dem_folder, dem_f),
                os.path.join(ref_folder, row.ref),
                method="CONTOUR", cell_size=cellsize, mask=msk
            )
    
    # Produce DEM
    thrds = [mp.Process(
        target=prod_dem, name='th-{}'.format(str(i+1)),
        args=(dfs[i],)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()


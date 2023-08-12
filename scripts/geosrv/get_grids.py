"""
Create Reference GRIDS for each level
"""

import os
import pandas as pd
import geopandas as gp

from glass.smp.obj  import fishnet
from glass.rd.shp   import shp_to_obj
from glass.wt.shp   import obj_to_shp
from glass.dtt.torst import shp_to_rst
from glass.wenv.grs import run_grass
from glass.pys.oss    import mkdir
from glass.pd.cols  import del_cols_notin_ref
from glass.wt.sql   import df_to_db
from glass.sql.tbl import drop_tbldata
from glass.prop.ext import featext_to_dfcols

if __name__ == '__main__':
    # Get parameters
    ref_geom = '/home/jasp/mrgis/flainar_serv/pt_cim_v4.shp'
    idcol    = 'cimid'
    out_grid = '/home/jasp/mrgis/flainar_serv/beautiful_grid.shp'

    db = 'eow-db-contents'
    grid_tbl = 'grids'

    lvl = 4
    epsg = 3763

    setdb = 'flainar'

    # Delete existent GRIDS
    drop_tbldata(db, grid_tbl, dbset=setdb)

    # Reference data to DataFrame
    ref_df = shp_to_obj(ref_geom)
    ref_df = featext_to_dfcols(ref_df, 'geometry')

    # Get Workspace for GRASS GIS
    workspace = mkdir(os.path.join(
        os.path.dirname(ref_geom),
        'grid_pro'
    ), overwrite=True)

    # Produce GRIDS for each level
    cols = ["sid", "level", "geom", "cim"]
    cols_b = {
        "b_sid" : "sid", "b_level" : "level",
        "b_cim" : "cim"
    }

    main_df = pd.DataFrame(columns=cols)

    # Do it for each reference feature in ref_geom
    for idx, row in ref_df.iterrows():
        e = 1

        # Export Reference Feature to file
        # Reference = level 1
        nutdf = gp.GeoDataFrame(
            pd.DataFrame(
                [[1, 1, row.geometry, row[idcol]]],
                columns=cols
            ), crs='EPSG:{}'.format(str(epsg)),
            geometry="geom"
        )

        # Add level 1 feature to main table
        main_df = main_df.append(nutdf, ignore_index=True, sort=False)

        nutshp = obj_to_shp(nutdf, 'geom', epsg, os.path.join(
            workspace, 'fgrid_{}_1.shp'.format(row[idcol])
        ))

        # Create Reference raster
        rref = shp_to_rst(nutshp, None, 10, 0, os.path.join(
            workspace, 'rnut_{}.tif'.format(row[idcol])
        ))

        # Create GRASS GIS Session
        loc_name='loc' + row[idcol]
        gbase = run_grass(workspace, location=loc_name, srs=rref)

        import grass.script.setup as gsetup

        gsetup.init(gbase, workspace, loc_name, 'PERMANENT')

        from glass.it.shp     import grs_to_shp, shp_to_grs
        from glass.gp.ovl.grs import grsintersection

        grsnut = shp_to_grs(nutshp, 'frefshp', asCMD=True)

        # For each level (excluding level 1) - create reference grid and
        # add it to main table
        for i in range(1, lvl):
            e = e * 2

            fnet = fishnet(
                (row.minx, row.maxy), (row.maxx, row.miny),
                x=(row.maxx - row.minx) / e,
                y=(row.maxy - row.miny) / e, epsg=epsg
            )
            fnet['sid']   = fnet.index
            fnet['level'] = i + 1
            fnet['cim']   = row[idcol]

            # Export GRID to File
            ffnet = obj_to_shp(fnet, 'geom', epsg, os.path.join(
                workspace, f'fnet_{row[idcol]}_{str(i + 1)}.shp'
            ))

            # Import to GRASS
            grs_ffnet = shp_to_grs(ffnet, f'fnet_{row[idcol]}')

            # Intersection
            i_ffnet = grsintersection(
                grsnut, grs_ffnet,
                f'res_{row[idcol]}_{str(i + 1)}', cmd=True)

            # Export
            clp_ffnet = grs_to_shp(i_ffnet, os.path.join(
                workspace, f'fgrid_{row[idcol]}_{str(i + 1)}.shp'
            ), 'area')

            clpfnet = shp_to_obj(clp_ffnet, outgeom='geom')
            clpfnet = del_cols_notin_ref(clpfnet, list(cols_b.keys()), geomCol="geom")
            clpfnet.rename(columns=cols_b, inplace=True)

            main_df = main_df.append(clpfnet, ignore_index=True, sort=False)
    
    main_df['id']    = main_df.index
    main_df['areag'] = main_df.geom.area
    main_df          = main_df[main_df.areag > 1]

    main_df.drop(['sid', 'areag'], axis=1, inplace=True)

    # Send data to database
    df_to_db(
        db, main_df, grid_tbl, append=True, api='psql',
        epsg=epsg, geomType="Polygon", colGeom='geom',
        dbset=setdb
    )

    obj_to_shp(main_df, 'geom', epsg, out_grid)


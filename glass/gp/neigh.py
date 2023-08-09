"""
neighborhood analysis
"""


def find_neighbords_cells(grid, otbl):
    """
    Este procedimento considera uma grelha vetorial regular e 
    encontra para cada célula os seus oito vizinhos tendo em 
    conta a dimensão da célula
    """

    import geopandas as gp

    from glass.gobj     import create_polygon
    from glass.rd.shp   import shp_to_obj
    from glass.pys.oss  import fprop
    from glass.prop.ext import featext_to_dfcols
    from glass.prop.prj import get_epsg
    from glass.sql.db   import create_pgdb
    from glass.wt.sql   import df_to_db
    from glass.sql.q    import q_to_obj
    from glass.wt       import obj_to_tbl

    epsg = get_epsg(grid)

    grid_df = shp_to_obj(grid)
    grid_df = featext_to_dfcols(grid_df, 'geometry')

    # Get Cellsize
    # Distance between topleft and bottomleft
    grid_df['height'] = ((
        grid_df.minx - grid_df.minx)**2 + (grid_df.maxy - grid_df.miny
    )**2)**0.5

    # Distance between topleft and topright
    grid_df['width'] = ((
        grid_df.maxx - grid_df.minx)**2 + (grid_df.maxy - grid_df.maxy
    )**2)**0.5

    # Get boundary including neigbords
    neighbor_grid = []
    neighbor_geom = []
    for idx, row in grid_df.iterrows():
        # Get Polygon including 8 neigbors
        top    = row.maxy + row.height
        left   = row.minx - row.width
        bottom = row.miny - row.height
        right  = row.maxx + row.width
        neig_poly = create_polygon([
            (left, top), (left, bottom),
            (right, bottom), (right, top)
        ], api='shapely')
    
        neighbor_grid.append([row.cellid, top, left, bottom, right])
        neighbor_geom.append(neig_poly)
    
    neighbor_grid = gp.GeoDataFrame(
        neighbor_grid,
        columns=['cid', 'top', 'left', 'bottom', 'right'],
        crs=f"EPSG:{str(epsg)}", geometry=neighbor_geom
    )

    # Create database
    db = create_pgdb(fprop(otbl, 'fn'))

    # Send data to database
    grid_tbl = df_to_db(
        db, grid_df, 'grid', api='psql',
        epsg=epsg, geomType='Polygon',
        colGeom='geometry'
    )
    neig_tbl = df_to_db(
        db, neighbor_grid, 'cells_box', api='psql', epsg=epsg,
        geomType='Polygon', colGeom='geometry'
    )

    neighbor_tbl = q_to_obj(db, (
        "SELECT jtbl.cellid, mtbl.cid AS isneighbor "
        f"FROM {neig_tbl} AS mtbl INNER JOIN ("
            "SELECT cellid, ST_Centroid(geom) AS geom "
            f"FROM {grid_tbl}"
        ") AS jtbl "
        "ON ST_ContainsProperly(mtbl.geom, jtbl.geom) "
        "WHERE mtbl.cid <> jtbl.cellid"
    ))

    obj_to_tbl(neighbor_tbl, otbl)

    return otbl


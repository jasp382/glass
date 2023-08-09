"""
Tools for sampling
"""
import random

from glass.pys import execmd

"""
Random Points
"""

def get_random_points_inside_polygon(npnt, poly, epsg, bounds=None):
    """
    Return a shapefile with random points
    inside a given polygon

    polygon = shapely geometry
    """

    import random         as rdn
    import geopandas      as gp
    from shapely.geometry import Point

    pnts = []

    # Get bounds
    left, bottom, right, top = list(poly.bounds) if not bounds \
        else bounds
    
    # Get Ranges
    xrng = right - left
    yrng = top - bottom

    while len(pnts) < npnt:
        # generate a random x and y for each point
        x = left + rdn.random() * xrng
        y = bottom + rdn.random() * yrng

        p = Point(x, y)

        if poly.contains(p):
            pnts.append(p)
    
    gdf = gp.GeoDataFrame(
        {'pid' : list(range(1, npnt + 1)), 'geom' : pnts},
        crs=f'EPSG:{str(epsg)}', geometry='geom'
    )

    return gdf


def get_randpnt_in_circle(df, radius, geomcol, epsg, radius_is_col=None):
    """
    For each row in dataframe,
    return the coordinates of a Random Point in a circle.
    
    The circle as a radius specified by the variable radius
    and a center given by the dataframe geometry
    """

    import numpy as np

    from glass.it.pd import pnt_dfwxy_to_geodf
    
    # Get X | Y
    if type(geomcol) == str:
        df["fx"], df["fy"] = df[geomcol].x, df[geomcol].y
    else:
        df["fx"], df["fy"] = df[geomcol[0]], df[geomcol[1]]

    # Random angle
    df["alpha"] = 2 * np.pi * np.random.random(df.shape[0])

    # Random radius
    if radius_is_col:
        df["rradius"] = df[radius] * np.sqrt(np.random.random(df.shape[0]))
    else:
        df["rradius"] = radius * np.sqrt(np.random.random(df.shape[0]))

    # Get coordinates
    df['nx'] = df.rradius * np.cos(df["alpha"]) + df.fx
    df['ny'] = df.rradius * np.sin(df["alpha"]) + df.fy

    # Go for geometry
    dcols = ['fx', 'fy', 'alpha', 'rradius']

    if type(geomcol) == str:
        dcols.append(geomcol)
    
    df.drop(dcols, axis=1, inplace=True)

    df = pnt_dfwxy_to_geodf(df, 'nx', 'ny', epsg)
    
    return df


def get_random_point(minX, maxX, minY, maxY):
    """
    Create a Single Random Point
    """
    
    from glass.gobj import new_pnt
    
    x = minX + (random.random() * (maxX - minX))
    y = minY + (random.random() * (maxY - minY))
    
    pnt = new_pnt(x, y)
    
    return pnt


def gen_near_random_points(row):
    """
    Generate 20 points near x and y

    Return result as MultiPoint
    """

    from shapely.geometry import MultiPoint

    mp = [(row.x, row.y)]
    
    for i in range(20):
        plx = random.randint(0, 1)
        ply = random.randint(0, 1)
        
        dx = random.randint(1, 20)
        dy = random.randint(1, 20)
        
        cx = row.x + dx if plx else row.x - dx
        cy = row.y + dy if ply else row.y - dy
        
        mp.append((cx, cy))
    
    row["geometry"] = MultiPoint(mp)
    
    return row


def grs_random_points(inShp, nPoints, outShp, npoints_in_all_poly=None, cmd=None):
    """
    Generate Random Points Feature Class
    """
    
    if not cmd:
        from grass.pygrass.modules import Module

        fl = 'a' if npoints_in_all_poly else ''
        
        aleatorio = Module(
            "v.random", output=outShp, npoints=nPoints,
            restrict=inShp, flags=fl,
            overwrite=True, run_=False
        )
        aleatorio()
    
    else:
        fl = '-a ' if npoints_in_all_poly else ''

        ocmd = execmd((
            f"v.random output={outShp} npoints={str(nPoints)} "
            f"restrict={inShp} {fl}"
            "--overwrite --quiet"
        ))
        
    return outShp


def sample_to_points(points, col_name, rst):
    """
    v.what.rast - Uploads raster values at positions of vector
    points to the table.
    """
    
    from grass.pygrass.modules import Module
    
    m = Module(
        "v.what.rast", map=points, raster=rst,
        column=col_name, run_=False, quiet=True
    )
    
    m()


def rst_random_pnt(rst, npnt, outvec):
    """
    Creates a raster map layer and vector point map containing
    randomly located points.
    """
    
    from grass.pygrass.modules import Module

    m = Module(
        "r.random", input=rst, npoints=npnt, vector=outvec,
        overwrite=True, run_=False, quiet=True
    ); m()
    
    return outvec


def pg_random_points(constrain, npoints, out_random):
    """
    Generate Random Points using PostgreSQL
    """

    from glass.sql.db  import create_pgdb
    from glass.rd.shp  import shp_to_obj
    from glass.pys.oss import fprop
    from glass.sql.q   import q_to_ntbl
    from glass.it.shp  import dbtbl_to_shp

    # Create database
    work_db = create_pgdb(fprop(out_random, 'fn'))

    # Get constrains data
    consdf = shp_to_obj(constrain)


    # create random points for each feature in constrain
    qs = []
    for idx, row in consdf.iterrows():
        # Get constrain geometry
        geom_wkt = row.geometry.wkt
    
        # Create random points query
        rquery = (
            f"SELECT {str(idx)} AS idx, (ST_DumpPoints(ST_GeneratePoints("
                f"ST_GeomFromText('{geom_wkt}'), {str(npoints)}"
            "))).geom AS geom "
        )
        qs.append(rquery)

    # Create random points table
    random_tbl = q_to_ntbl(
        work_db, work_db, " UNION ALL ".join(qs)
    )
    # Export random points to file
    dbtbl_to_shp(work_db, random_tbl, 'geom', out_random)

    return out_random


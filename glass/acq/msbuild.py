"""
Microsoft Building Footprint
"""

import os
import mercantile
import pandas as pd
import geopandas as gpd

from tqdm import tqdm
from shapely.geometry import shape

from glass.prj.obj import df_prj
from glass.prop.prj import get_epsg
from glass.prop.ext import get_ext
from glass.pys.oss import fprop, mkdir
from glass.it.shp import shps_to_gpkg

MS_BUILD = "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv"


def get_building_footprint(roi_shp, outbuild):
    """
    Extract buildings for a region of interest
    """
    
    import tempfile
    
    from glass.wt.shp import obj_to_shp

    """
    ## Step 1 - Define our area of interest (AOI)
    We define our area of interest (or AOI) as a GeoJSON
    geometry, then use the `shapely` library to get the bounding box.

    **Note**: the coordinate reference system for the GeoJSON should be "EPSG:4326", i.e. 
    in global lat/lon format.
    """

    epsg = get_epsg(roi_shp)

    minx, maxx, miny, maxy = get_ext(roi_shp, oepsg=4326)

    aoi_geom = {
        "coordinates" : [[
            [minx, maxy],
            [maxx, maxy],
            [maxx, miny],
            [minx, miny],
            [minx, maxy]
        ]],
        "type" : "Polygon"
    }

    aoi_shape = shape(aoi_geom)

    # Step 2 - Determine which tiles intersect our AOI
    # The dataset is organized by tiles
    quad_keys = set()
    for tile in list(mercantile.tiles(minx, miny, maxx, maxy, zooms=9)):
        quad_keys.add(mercantile.quadkey(tile))
    
    quad_keys = list(quad_keys)
    print(f"The input area spans {len(quad_keys)} tiles: {quad_keys}")

    """
    Step 3 - Download the building footprints for each tile that intersects our AOI and crop the results

    This is where most of the magic happens. We download all the building footprints for each tile that 
    intersects our AOI, then only keep the footprints that are _contained_ by our AOI.

    *Note*: this step might take awhile depending on how many tiles your AOI covers and how many 
    buildings footprints are in those tiles.
    """

    df = pd.read_csv(MS_BUILD, dtype=str)

    idx = 0
    combined_gdf = gpd.GeoDataFrame()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Download the GeoJSON files for each tile that intersects the input geometry
        tmp_fns = []
        for quad_key in tqdm(quad_keys):
            rows = df[df["QuadKey"] == quad_key]
            if rows.shape[0]:
                for i, row in rows.iterrows():
                    url = row["Url"]

                    df2 = pd.read_json(url, lines=True)
                    df2["geometry"] = df2["geometry"].apply(shape)

                    gdf = gpd.GeoDataFrame(df2, crs=4326)
                    fn = os.path.join(tmpdir, f"{quad_key}_{str(i)}.geojson")
                    tmp_fns.append(fn)
                    if not os.path.exists(fn):
                        gdf.to_file(fn, driver="GeoJSON")
            #elif rows.shape[0] > 1:
                #raise ValueError(f"Multiple rows found for QuadKey: {quad_key}")
            else:
                print(f"QuadKey not found in dataset: {quad_key}")

        # Merge the GeoJSON files into a single file
        for fn in tmp_fns:
            gdf = gpd.read_file(fn)  # Read each file into a GeoDataFrame
            gdf = gdf[gdf.geometry.within(aoi_shape)]  # Filter geometries within the AOI
            gdf['id'] = range(idx, idx + len(gdf))  # Update 'id' based on idx
            idx += len(gdf)
            combined_gdf = pd.concat([combined_gdf,gdf],ignore_index=True)
    
    # Step 4 - Save the resulting footprints to file
    combined_gdf = df_prj(combined_gdf, epsg)

    obj_to_shp(combined_gdf, 'geometry', epsg, outbuild)

    return outbuild



def msbuild_to_gpkg(roi, out):
    """
    Microsoft Building Footprint to GeoPackage
    """

    from glass.dtt.mge import shps_to_shp

    tmpfld = mkdir(os.path.join(
        os.path.dirname(out),
        fprop(out, 'fn')
    ))

    epsg = get_epsg(roi)

    """
    ## Step 1 - Define our area of interest (AOI)
    We define our area of interest (or AOI) as a GeoJSON
    geometry, then use the `shapely` library to get the bounding box.

    **Note**: the coordinate reference system for the GeoJSON should be "EPSG:4326", i.e. 
    in global lat/lon format.
    """

    minx, maxx, miny, maxy = get_ext(roi, oepsg=4326)

    # Step 2 - Determine which tiles intersect our AOI
    # The dataset is organized by tiles
    quad_keys = set()
    for tile in list(mercantile.tiles(minx, miny, maxx, maxy, zooms=9)):
        quad_keys.add(mercantile.quadkey(tile))
    
    quad_keys = list(quad_keys)
    print(f"The input area spans {len(quad_keys)} tiles")

    """
    Step 3 - Download the building footprints for each tile that intersects our AOI and crop the results

    This is where most of the magic happens. We download all the building footprints for each tile that 
    intersects our AOI, then only keep the footprints that are _contained_ by our AOI.

    *Note*: this step might take awhile depending on how many tiles your AOI covers and how many 
    buildings footprints are in those tiles.
    """

    df = pd.read_csv(MS_BUILD, dtype=str)

    df = df[df.QuadKey.isin(quad_keys)]

    gjsons = []

    for _, row in df.iterrows():
        gdf = pd.read_json(row.Url, lines=True)

        gdf["geometry"] = gdf["geometry"].apply(shape)

        gdf = gpd.GeoDataFrame(gdf, crs="EPSG:4326", geometry="geometry")

        if epsg != 4326:
            gdf = df_prj(gdf, epsg)

        gjson = os.path.join(tmpfld, f'qk_{row.QuadKey}.geojson')
        gdf.to_file(gjson, driver="GeoJSON")

        gjsons.append(gjson)

    shps_to_shp(gjsons, out)

    return out



def msbuild_by_loc(ogpkg, location='UnitedKingdom'):
    """
    Download Microsoft Building Footprint data
    by location
    """

    dataset_links = pd.read_csv("https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv")
    cnt_links = dataset_links[dataset_links.Location == location]

    tmpfld = mkdir(os.path.dirname(ogpkg), timerand=True)

    for _, row in cnt_links.iterrows():
        df = pd.read_json(row.Url, lines=True)

        df["geometry"] = df["geometry"].apply(shape)

        gdf = gpd.GeoDataFrame(df, crs=4326)

        gdf.to_file(os.path.join(tmpfld, f'qk_{row.QuadKey}.geojson'), driver="GeoJSON")

    shps_to_gpkg(tmpfld, ogpkg, shp_ff='.geojson')

    return ogpkg


"""
Tools related with osm Files
"""

def osm_countries(out_shp):
    """
    Get the boundary representing areas with OSM data in every
    OSM PBF country file in GeoFabrik
    """

    import os; import codecs
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import MultiPolygon, Polygon
    from glass.cons.osm    import osm_files
    from glass.to.web      import get_file
    from glass.geo.gt.toshp    import df_to_shp
    from glass.pyt.oss     import del_file
    
    url = 'http://download.geofabrik.de/{}/{}.poly'
    url_russia = 'http://download.geofabrik.de/russia.poly'

    countries_boundaries = []
    for c in osm_files:
        for _c in osm_files[c]:
            # Get poly file
            ff = get_file(
                url.format(c, _c) if c != 'russia' else url_russia,
                os.path.join(
                    os.path.dirname(out_shp), "{}_{}.poly".format(
                        c, _c.replace('/', '_')
                    ) if c != 'russia' else "russia.poly"
                )
            )

            # Get Polygon Coordinates
            in_ring = False
            coords = []

            with open(ff, 'r') as txt:
                i = 0
                for l in txt.readlines():
                    if i == 0:
                        # first line is junk
                        i += 1
                        continue
                    
                    elif i == 1:
                        # second line is the first polygon ring.
                        coords.append([[], []])
                        ring = coords[-1][0]
                        in_ring = True
                        i += 1
                    
                    elif in_ring and l.strip() == 'END':
                        # we are at the end of a ring, perhaps with more to come.
                        in_ring = False
                    
                    elif in_ring:
                        # we are in a ring and picking up new coordinates.
                        pnt = l.strip().split('   ')
                        ring.append((float(pnt[0]), float(pnt[1])))
                    
                    elif not in_ring and l.strip() == 'END':
                        # we are at the end of the whole polygon.
                        break
                    
                    elif not in_ring and l.startswith('!'):
                        # we are at the start of a polygon part hole.
                        coords[-1][1].append([])
                        ring = coords[-1][1][-1]
                        in_ring = True
                    
                    elif not in_ring:
                        # we are at the start of a polygon part.
                        coords.append([[], []])
                        ring = coords[-1][0]
                        in_ring = True
                
                polygon = MultiPolygon(coords)
            
            countries_boundaries.append([c, _c, polygon])
            del_file(ff)
    
    countries_boundaries = gpd.GeoDataFrame(
        pd.DataFrame(countries_boundaries, columns=['continent', 'country', 'geometry']),
        crs={'init' : 'epsg:4326'}, geometry='geometry'
    )

    return df_to_shp(countries_boundaries, out_shp)

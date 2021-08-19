"""
OSM File to PostgreSQL database
"""

if __name__ == '__main__':
    osm_file = '/home/osmtolulc/mrgis/europe-latest.osm.pbf'
    db = 'osm_europe'

    from glass.g.it.db import osm_to_psql

    osm_to_psql(osm_file, db)


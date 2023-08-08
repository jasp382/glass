"""
OSM File to PostgreSQL database
"""

if __name__ == '__main__':
    osm_file = '/mnt/disk1/jasp/osm2lulc/europe-latest.osm.pbf'
    db = 'osm_europe'

    from glass.it.db import osm_to_psql

    osm_to_psql(osm_file, db)


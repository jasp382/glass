"""
OSM File to PostgreSQL database
"""

if __name__ == '__main__':
    osm_file = '/home/osmtolulc/mrgis/europe-latest.osm.pbf'
    db = 'osm_europe'

    from glass.gql.to.osm import osm_to_psql

    osm_to_psql(osm_file, db)


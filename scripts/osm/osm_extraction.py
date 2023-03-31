"""
Clip OSM File using OSMOSIS
"""

from glass.gp.ovl.osm import osm_extraction

if __name__ == "__main__":
    ia = '/mnt/disk1/jasp/ddpaper/area4S2tiles.tif'
    osmfile = '/mnt/disk3/jasp/osmbigfiles/osm_world.pbf'
    out = '/mnt/disk1/jasp/ddpaper/osm_data.xml'

    osm_extraction(
        ia, osmfile, out,
        each_feat=None, epsg=None,
        outbasename=None
    )


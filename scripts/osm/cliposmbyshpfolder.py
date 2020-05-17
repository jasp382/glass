"""
Clip OSM File for each shapefile in one folder
"""

if __name__ == '__main__':
    from glass.gp.ovl.osm import osmextract_foreachshp

    osmfile  = '/mnt/disk1/jasp/osm2lulc/europe-latest.osm.pbf'
    clipshps = '/mnt/disk1/jasp/osm2lulc/lmt_basel'

    outfolder = '/mnt/disk1/jasp/osm2lulc/osm_parts'

    bname = 'osmbasel'

    osmextract_foreachshp(osmfile, clipshps, outfolder, bname=bname)


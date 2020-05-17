"""
Clip Feature Class using as clip features each file of one folder
"""

if __name__ == "__main__":
    from glass.gp.ovl.clipp import clipshp_shpinfolder

    in_shp = '/home/jasp/mystuff/dgt_caeosm/osmdata/urbanosm_v3_diss.shp'

    clipshps = '/home/jasp/mystuff/dgt_caeosm/lmt/refparts'

    outfolder = '/home/jasp/mystuff/dgt_caeosm/osmdata/osmshp_v3'

    bname = 'uosmv3'

    clipshp_shpinfolder(in_shp, clipshps, outfolder, bname=bname)


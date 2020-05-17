"""
Clip Feature Class using as clip features each file of one folder
"""

if __name__ == "__main__":
    from glass.gp.ovl.clipp import clipshp_shpinfolder

    in_shp = '/home/jasp/mystuff/dgt/builtup_2018.shp'

    clipshps = '/home/jasp/mystuff/dgt/refparts'

    outfolder = '/home/jasp/mystuff/dgt/builtup'

    bname = 'builtup'

    clipshp_shpinfolder(in_shp, clipshps, outfolder, bname=bname)


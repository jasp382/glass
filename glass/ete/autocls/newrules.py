"""
Methods to help find new rules to filter OSM data
used for training
"""


def idxdist_by_class(shp, lulc_col, idxs_folder, ofolder):
    """
    For each class in a Feature class, get rasters
    with the distribution of several radiometric
    indexes in that class
    """

    import os

    from glass.pys.oss   import lst_folders_subfiles, mkdir
    from glass.pys.tm    import now_as_str
    from glass.dtt.split import split_shp_by_attr
    from glass.wenv.grs  import run_grass

    # List images folder
    imgs = lst_folders_subfiles(idxs_folder, files_format='.tif')

    ikeys = list(imgs.keys())
    refrst = imgs[ikeys[0]][0]

    # Create Workspace
    ws = mkdir(os.path.join(ofolder, now_as_str()), overwrite=True)

    # Split Shapefile
    gpkg = os.path.join(ws, 'pureobj.gpkg')
    shps = split_shp_by_attr(
        shp, lulc_col, ws, _format='.gpkg',
        outname='pureobj', valinname=True
    )

    # Create GRASS GIS Session
    loc = 'loc_histo'

    gs = run_grass(ws, location=loc, srs=refrst)

    import grass.script.setup as gsetup
    gsetup.init(gs, ws, loc, 'PERMANENT')

    from glass.it.shp    import shp_to_grs
    from glass.it.rst    import rst_to_grs, grs_to_rst
    from glass.dtt.torst import grsshp_to_grsrst
    from glass.rst.alg   import grsrstcalc

    for c in shps:
        shp_to_grs(gpkg, lyrname=shps[c], asCMD=True)

        shps[c] = grsshp_to_grsrst(shps[c], 1, f"rst_{shps[c]}")
    
    # Import all rasters
    for day in imgs:
        for i in range(len(imgs[day])):
            imgs[day][i] = rst_to_grs(imgs[day][i])
    
    # Filter IDX by class and export
    out = {}
    for cls in shps:
        out[cls] = {}
        for day in imgs:
            out[cls][day] = []
            for r in imgs[day]:
                frst = grsrstcalc(f"{shps[cls]} * {r}", f"c{str(cls)}_{r}")
                tifrst = grs_to_rst(frst, os.path.join(
                    ofolder, f'{frst}.tif'
                ), as_cmd=True, rtype=float)

                out[cls][day].append(tifrst)
    
    return out


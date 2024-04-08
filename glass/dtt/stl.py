"""
Handling Sentinel-2 data
"""

def unzip_img(zip_file, out_folder, bands=None):
    """
    Unzip Sentinel-2 Image
    """

    import os
    from zipfile        import ZipFile

    from glass.pys      import obj_to_lst
    from glass.cons.sat import get_lwibands, bandsmap
    from glass.pys.oss  import copy_file

    bmap = bandsmap()
    intbands = get_lwibands() if not bands else obj_to_lst(bands)


    with ZipFile(zip_file, 'r') as zipo:
        zipff = zipo.namelist()

        rbands = {}
        for b in bmap:
            if bmap[b] not in intbands:
                continue

            for f in zipff:
                if b in f:
                    ob = os.path.join(out_folder, os.path.basename(f))

                    zipo.extract(f, out_folder, pwd=None)
                    copy_file(
                        os.path.join(out_folder, f), ob
                    )
                    rbands[bmap[b]] = ob

                    break
    
    return rbands


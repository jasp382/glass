"""
Handling Sentinel-2 data
"""

def unzip_img(zip_file, out_folder):
    """
    Unzip Sentinel-2 Image
    """

    import os
    from zipfile        import ZipFile
    from glass.cons.stl import get_ibands
    from glass.pys.oss  import copy_file

    intbands = get_ibands()


    with ZipFile(zip_file, 'r') as zipo:
        zipff = zipo.namelist()

        rbands = {}
        for b in intbands:
            for f in zipff:
                if b in f:
                    ob = os.path.join(out_folder, os.path.basename(f))

                    zipo.extract(f, out_folder, pwd=None)
                    copy_file(
                        os.path.join(out_folder, f), ob
                    )
                    rbands[b] = ob

                    break
    
    return rbands


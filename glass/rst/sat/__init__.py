


def lst_s2img_by_band(folder, bname=None, fformat=None):
    """
    List Sentinel-2 images files and organize data by band
    """

    from glass.pys.oss import lst_folders_subfiles
    from glass.cons.sat import get_lwibands

    fformat = '.tif' if not fformat else fformat

    imgs = lst_folders_subfiles(folder, filter_folder=bname, files_format=fformat)

    bandmap = get_lwibands()

    for f in imgs:
        d = {}

        for b in imgs[f]:
            for k in bandmap:
                if k in b:
                    d[k] = b
        
        imgs[f] = d
    
    return imgs


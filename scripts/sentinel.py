"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.gt.fmweb.sentinel import down_imgs

    in_shp = '/home/osmtolulc/mrgis/sentinel_pt/imgs_pt.shp'
    out_folder = '/home/osmtolulc/mrgis/sentinel_pt'

    down_imgs(in_shp, 'uuid', outFolder=out_folder)


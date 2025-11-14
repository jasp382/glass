"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.acq.stl import down_imgs

    imgs = '/mnt/x/autocls_e4/imgs_search/dimgs_2020.shp'

    imgid = 'uid'

    iname = 'name'

    ofolder = '/home/jasp/autocls/l2a_2020'

    down_imgs(imgs, imgid, iname, ofolder)


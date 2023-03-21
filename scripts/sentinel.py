"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.acq.stl import down_imgs_v2

    imgs = '/mnt/disk1/jasp/a2autocls2023/imgcmb/img_cmb18p.shp'

    imgid = 'uuid'

    ofolder = '/mnt/disk3/jasp/coimbra/src2018p'

    down_imgs_v2(imgs, imgid, ofolder=ofolder)


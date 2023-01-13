"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.acq.stl import down_imgs_v2

    imgs = '/mnt/disk1/jasp/a2autocls2023/sentinel/img_cmb18.shp'

    imgid = 'uuid'

    ofolder = '/mnt/disk3/jasp/sentinel_coimbra/src2018'

    down_imgs_v2(imgs, imgid, ofolder=ofolder)


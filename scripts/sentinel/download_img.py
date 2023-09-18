"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.acq.stl import down_imgs_v2

    imgs = '/mnt/g/autocls/sat_s2_porto/img_2018.shp'

    imgid = 'uuid'

    ofolder = '/home/jasp/s2img'

    down_imgs_v2(imgs, imgid, ofolder=ofolder)


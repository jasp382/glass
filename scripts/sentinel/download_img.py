"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.acq.stl import down_imgs_v2

    imgs = '/mnt/disk1/jasp/pmsig/img_to_down.shp'

    imgid = 'uuid'

    ofolder = '/mnt/disk1/jasp/pmsig'

    down_imgs_v2(imgs, imgid, ofolder=ofolder)


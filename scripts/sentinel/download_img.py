"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.acq.stl import down_imgs_v2

    imgs = '/mnt/e/water7/pilot_img/pilotimg.shp'

    imgid = 'uuid'

    ofolder = '/home/jakim/pilotimg2023'

    down_imgs_v2(imgs, imgid, ofolder=ofolder)


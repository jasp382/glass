"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.acq.stl import down_imgs_v2

    imgs = '/mnt/g/imgs2017.shp'

    imgid = 'uuid'

    ofolder = '/home/gisuser/autocls'

    down_imgs_v2(imgs, imgid, ofolder=ofolder)


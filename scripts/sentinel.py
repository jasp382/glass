"""
Download Sentinel-2 IMG
"""

if __name__ == '__main__':
    from glass.g.acq.sentinel import down_imgs

    in_shp = '/home/jasp/mrgis/sentinel_cmb/sentinel.shp'
    out_folder = '/home/jasp/mrgis/sentinel_cmb'

    down_imgs(in_shp, 'uuid', outFolder=out_folder)


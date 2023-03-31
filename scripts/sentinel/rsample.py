"""
Sentinel-2 Images
"""

from glass.rst.sat.rmp import resample_s2img_shp


if __name__ == "__main__":
    shp     = '/mnt/disk1/jasp/a2autocls2023/imgcmb/img_cmb18p.shp'

    folder  = '/mnt/disk3/jasp/coimbra/src2018p'

    ofolder = '/mnt/disk1/jasp/a2autocls2023/imgcmb/rmp2018p'

    #reflmt  = '/mnt/disk1/jasp/a2autocls2023/ref/lmt_terceira.shp'
    reflmt  = None

    resample_s2img_shp(shp, folder, ofolder, refgeo=reflmt)


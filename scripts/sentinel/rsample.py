"""
Sentinel-2 Images
"""

from glass.rst.sat.rmp import resample_s2img_shp


if __name__ == "__main__":
    shp = '/mnt/disk1/jasp/a2autocls2023/sentinel/img_cmb21.shp'

    folder = '/mnt/disk3/jasp/sentinel_coimbra/src2021'

    ofolder = '/mnt/disk1/jasp/a2autocls2023/imgcmb/rmp2021'

    resample_s2img_shp(shp, folder, ofolder)


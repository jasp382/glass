"""
Resample sentinel images in a given folder

Organize outputs by month
"""

import pandas as pd
import os
from glass.rd.shp import shp_to_obj
from glass.pys.tm import now_as_str
from glass.pys.oss import lst_ff, mkdir, del_folder
from glass.dtt.stl  import unzip_img
from glass.rst.sat.rmp  import resample_s2img


if __name__ == '__main__':
    ifolder = '/mnt/c/s2_coimbra21'

    ofolder = '/mnt/c/s2_vflores21'

    refrst = '/mnt/c/stdrst_valeflores.tif'

    imgs = lst_ff(ifolder, file_format='.zip', rfilename=True)

    _imgs = [[i] + i[:-4].split('_') for i in imgs]

    idf = pd.DataFrame(_imgs, columns=[
        'filename', 'satelite', 'sensor',
        'sensortime', 'n', 'r',
        'cellid', 'prodtime'
    ])

    idf['sensortime'] = pd.to_datetime(idf.sensortime, format='%Y%m%dT%H%M%S')
    idf['sensortime'] = idf.sensortime.dt.floor('s')
    idf['sensormonth'] = idf.sensortime.dt.month
    idf['prodtime'] = pd.to_datetime(idf.prodtime, format='%Y%m%dT%H%M%S')

    months = idf.sensormonth.unique()
    months.sort()

    for m in months:
        imgs = idf[idf.sensormonth == m]
    
        mf = mkdir(os.path.join(ofolder, f"m_{str(m)}"))
    
        for i, r in imgs.iterrows():
            resample_s2img(
                os.path.join(ifolder, r['filename']),
                refrst,
                ofolder,
                bands=['b02', 'b03', 'b04', 'b05', 'b06', 'b07', 'b08', 'b11', 'b12']
            )


"""
Clouds
"""

import os


def rm_clouds(bands, scl, ofolder):
    """
    Remove clouds from one Sentinel-2 image

    Clouds will have NoData Value
    """


    return ofolder


def rm_anyclouds(folder, bands, scl, ff, ofolder, noclouds_raster):
    """
    Considera uma pasta com imagens sentinel-2:

    - Na pasta existem bandas e ficheiros SCL;
    - Usando os ficheiros SCL, são indentificados todos os pixeis
    com nuvens independentemente da imagem;
    - É produzido um ficheiro raster em que as células com valor
    sao aquelas que não têm nuvens em nenhum momento;
    - Todas as bandas são reclassificadas, de modo a que qualquer 
    célula com nuvens (independentemente da imagem) apresente
    valor nodata.

    (e.g. uma imagem 08-09 sem nuvens, terá pixeis NoData
    se uma imagem de 12-12 tiver nuvens)
    """

    from glass.pys.oss  import lst_ff, fprop
    from glass.pys.tm   import now_as_str
    from glass.wenv.grs import run_grass
    from glass.rst.rcls import rcls_rules

    # list bands
    imgs = lst_ff(folder, file_format=ff, fnpart=bands)

    # List scl
    scls = lst_ff(folder, file_format=ff, fnpart=[scl])

    # Create GRASS GIS Session
    ws, loc = ofolder, f"loc_{now_as_str()}"

    grsb = run_grass(ws, location=loc, srs=imgs[0])
    
    import grass.script.setup as gsetup
    
    gsetup.init(grsb, ws, loc, 'PERMANENT')

    from glass.it.rst   import rst_to_grs, grs_to_rst
    from glass.rst.rcls import rcls_rst
    from glass.rst.alg  import grsrstcalc

    cldrules = rcls_rules({
        0  : 0, 1 : 0,
        2  : 'NULL', 3 : 'NULL',
        4  : 0, 5 : 0, 6 : 0, 7 : 0,
        8  : 'NULL', 9 : 'NULL',
        10 : 'NULL',
        11 : 0
    }, os.path.join(ws, loc, 'no_clouds.txt'))

    rscl = []
    for s in scls:
        # Add SCL to GRASS GIS
        _s = rst_to_grs(s, fprop(s, 'fn'))

        # Reclassify all files to get only things related to clouds
        rs = rcls_rst(_s, cldrules, f'rcls_{_s}', api='grass')
        _rs = grsrstcalc(rs, f'cp_{_s}')
    
        rscl.append(_rs)

    # One file with all clouds as nodata
    cloud_rst = grsrstcalc(" + ".join(rscl), 'no_clouds')

    # Export clouds
    rcld = grs_to_rst(cloud_rst, noclouds_raster, rtype=int)

    return ofolder


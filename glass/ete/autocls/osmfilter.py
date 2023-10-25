"""
Tools to filter OSM2LULC results for training
"""

import os

from glass.it.rst   import rst_to_grs, grs_to_rst
from glass.pys.oss  import fprop, mkdir
from glass.rst.alg  import grsrstcalc
from glass.wenv.grs import run_grass


def rm_mixed_pixels(osmlulc, osmlyr, lulc_col, refimg, out):
    """
    Remove mixed pixels in OSM2LULC results
    """

    from glass.dtt.cg.sql import polyg_to_lines
    from glass.dtt.split  import split_shp_by_attr
    from glass.dtt.torst  import shp_to_rst, grsshp_to_grsrst
    from glass.it.db      import shp_to_psql
    from glass.it.shp     import shp_to_grs
    from glass.prj        import proj
    from glass.prop.prj   import get_epsg, shp_epsg
    from glass.pys.tm     import now_as_str
    from glass.rst.mos    import rsts_to_mosaic
    from glass.rst.rcls   import null_to_value, set_null
    from glass.sql.db     import create_pgdb

    # Setup workspace and GRASS GIS Session
    # Check if outfolder exists
    ws = os.path.dirname(out)
    if not os.path.exists(ws):
        mkdir(ws, overwrite=None)

    """
    Start GRASS GIS Session
    """
    loc = f'loc_{now_as_str()}'
    grsb = run_grass(
        ws, grassBIN='grass78', location=loc,
        srs=refimg
    )

    import grass.script.setup as gsetup
    
    gsetup.init(grsb, ws, loc, 'PERMANENT')

    # Temp Geopackage
    tmpgpkg = os.path.join(ws, loc, 'tmpdata.gpkg')

    # Re-project data if necessary
    iepsg = shp_epsg(osmlulc, lyrname=osmlyr)
    oepsg = get_epsg(refimg)

    if iepsg != oepsg:
        osmlulc = proj(
            osmlulc, tmpgpkg, oepsg, inEPSG=iepsg,
            api="ogr2ogr", ilyr=osmlyr, olyr=osmlyr
        )
    
    # Create DB
    db = create_pgdb(fprop(out, 'fn'), overwrite=True)

    # Send data to the database
    geotbl = shp_to_psql(
        db, osmlulc, api='ogr2ogr',
        lyrname={osmlulc: osmlyr}
    )

    # Transform polygons into lines
    linelyr = 'lulc_lines'
    linetbl = polyg_to_lines(
        db, geotbl, 'geom', tmpgpkg,
        out_is_file=True, olyr=linelyr
    )

    # Add data to GRASS GIS
    grslnh = shp_to_grs(linetbl, lyrname=linelyr, asCMD=True)

    # LULC Classes to Raster
    # First, each class to a new layer
    lclyrs = split_shp_by_attr(
        osmlulc, lulc_col,
        tmpgpkg, ilyr=osmlyr, outname='lulc',
        valinname=True
    )

    # Second convert each layer to raster
    for shp in lclyrs:
        lclyrs[shp] = shp_to_rst(
            tmpgpkg, 1, 10, 0,
            os.path.join(ws, loc, f'rst_lulc_{shp}.tif'),
            rst_template=refimg, lyrname=lclyrs[shp],
            api='gdal', rtype=int, dtype='Byte'
        )
    
    # Lines to Raster
    lnhrst = grsshp_to_grsrst(grslnh, 1, 'rstlines', cmd=True)

    null_to_value(lnhrst, 0, as_cmd=True)
    set_null(lnhrst, 1, ascmd=True)

    # For each class
    # Add it to GRASS GIS
    # Remove Mixed cells

    # Reclassify: class present = 1; ausence=0
    for cls in lclyrs:
        lclyrs[cls] = rst_to_grs(lclyrs[cls], as_cmd=True)

        lclyrs[cls] = grsrstcalc(f"{lclyrs[cls]} + {lnhrst}", f"{lclyrs[cls]}_v1")

        null_to_value(lclyrs[cls], 0, as_cmd=True)

    # Sum all class rasters to know were we have
    # cells with more than one class
    sumrst = grsrstcalc(
        " + ".join(list(lclyrs.values())),
        'overlaycells'
    )
    fcells = grsrstcalc(
        f"if({sumrst} > 1, null(), 0)",
        'cellsmantain'
    )

    # For each class, remove cells with more than one class
    for cls in lclyrs:
        set_null(lclyrs[cls], 0, ascmd=True)
        lclyrs[cls] = grsrstcalc(
            f"{lclyrs[cls]} + {fcells} + {cls} - 1",
            f"{lclyrs[cls]}_v2"
        )

    # Create final raster
    frst = rsts_to_mosaic(list(lclyrs.values()), fprop(out, 'fn'))

    # Export final result
    grs_to_rst(
        frst, out, as_cmd=False, rtype=int,
        dtype='UInt16', nodata=0
    )

    return out


def apply_idxfilter(lulc_rst, idxrst, idx_rules, fraster, watercls=None):
    """
    Apply filters to OSM2LULC Results based
    on radiometric indexes
    """

    import numpy as np

    from glass.rd.rst import rst_to_array
    from glass.prop.rst import get_nodata
    from glass.pys.oss import fprop
    
    from glass.pys.tm import now_as_str
    from glass.rd import tbl_to_obj
    from glass.rd.js import json_to_obj

    # Get Indexes list
    idxs = tbl_to_obj(idxrst['xlsx'], sheet=idxrst['sheet'])

    idxs.set_index(idxrst['dayscol'], inplace=True)

    idxs = idxs.to_dict(orient='index')

    # Get filter rules
    rules = json_to_obj(idx_rules)

    _rules = {int(k) : rules[k] for k in rules}

    ndays = len(list(idxs.keys()))

    for c in _rules:
        for idx in _rules[c]:
            if not _rules[c][idx]: continue

            _rules[c][idx]['nimgs'] = ndays if _rules[c][idx]['nimgs'] == 'all' \
                else int(_rules[c][idx]['nimgs'])
    
    # Check if outfolder exists
    ws = os.path.dirname(fraster)
    if not os.path.exists(ws):
        mkdir(ws, overwrite=None)
    
    """
    Start GRASS GIS Session
    """
    loc = f'loc_{now_as_str()}'
    grsb = run_grass(
        ws, grassBIN='grass78', location=loc,
        srs=lulc_rst
    )

    import grass.script.setup as gsetup
    
    gsetup.init(grsb, ws, loc, 'PERMANENT')

    # Identificar classes existentes no raster com as classes de LULC
    lulc_img = rst_to_array(lulc_rst)

    ndval = get_nodata(lulc_rst)

    lulc_class = [v for v in np.unique(lulc_img) if v in _rules and v != ndval]

    # Send all rasters to GRASS GIS
    lulc_grs = rst_to_grs(lulc_rst, fprop(lulc_rst, 'fn'))

    for d in idxs:
        for k in idxs[d]:
            idxs[d][k] = rst_to_grs(idxs[d][k], fprop(idxs[d][k], 'fn'))
    
    # Para cada classe, índice e data, criar um ficheiro 
    # que indica se o pixel deve ser considerado 
    # para treino (1) ou não (0)
    mask_by_class_day_idx = {}

    for cls in lulc_class:
        mask_by_class_day_idx[cls] = {}
        for d in idxs:
            mask_by_class_day_idx[cls][d] = {}
            for k in idxs[d]:
                if not _rules[cls][k]: continue
            
                form = (
                    f"if({lulc_grs} == {str(cls)} && "
                    f"{idxs[d][k]} >= {_rules[cls][k]['min']} && "
                    f"{idxs[d][k]} <= {_rules[cls][k]['max']}, "
                    "1, 0)"
                )
            
                outmask = grsrstcalc(form, f'mask_{cls}_{k}_{d}')
            
                mask_by_class_day_idx[cls][d][k] = outmask
            
                grs_to_rst(outmask, os.path.join(
                    ws, loc,
                    f'{outmask}.tif'
                ), rtype=int)
    
    # Para cada classe e índice, criar um ficheiro que 
    # indica se o pixel deve ser incluído no treino (1) 
    # ou não (0), tendo em conta as várias máscaras obtidas 
    # para essa classe e índice em cada uma das datas consideradas
    cls_masks = {}

    for cls in mask_by_class_day_idx:
        cls_masks[cls] = {}
    
        for d in mask_by_class_day_idx[cls]:
            for idx in mask_by_class_day_idx[cls][d]:
                if idx not in cls_masks[cls]:
                    cls_masks[cls][idx] = []
            
                cls_masks[cls][idx].append(mask_by_class_day_idx[cls][d][idx])
    
    for cls in cls_masks:
        for idx in cls_masks[cls]:
            cntrst = grsrstcalc(
                " + ".join(cls_masks[cls][idx]),
                f'clsidxcount_{cls}_{idx}', ascmd=True
            )
        
            cls_masks[cls][idx] = grsrstcalc(
                f"if({cntrst} >= {_rules[cls][idx]['nimgs']}, 1, 0)",
                f'clsidxmask_{cls}_{idx}', ascmd=True
            )
    
    # Obter máscara binária final para cada classe
    for cls in cls_masks:
        ifr = [f"{cls_masks[cls][idx]} == 1" for idx in cls_masks[cls]]
    
        exp = f"if({' && '.join(ifr)}, 1, 0)"
    
        cls_masks[cls] = grsrstcalc(exp, f"clsmask_{cls}", ascmd=True)
    
    # Obter ficheiro que indica as classes a considerar no 
    # treino - neste raster, o valor 0 indica que o pixel 
    # não deve ser considerado no treino.
    ifs = []

    for c in cls_masks:
        exp = (
            f"if({cls_masks[c]} == 1, "
            f"{str(c)}, "
            f"{'0' if not len(ifs) else ifs[len(ifs)-1]})"
        )
    
        ifs.append(exp)

    rfnl = grsrstcalc(
        ifs[-1],
        fprop(fraster, 'fn'), ascmd=True
    )

    # Place waters with low NDWI
    # if water cls
    if watercls:

        exp = (
            f"if({lulc_grs} == {watercls} && {rfnl} == 0, "
            f"99, {rfnl})"
        )
        rfnl = grsrstcalc(exp, f"{rfnl}_watercorr", ascmd=True)

    grs_to_rst(
        rfnl, fraster, as_cmd=True,
        rtype=int, nodata=0
    )

    return fraster


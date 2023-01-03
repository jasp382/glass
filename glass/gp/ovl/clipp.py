"""
Clipping tools
"""

import os

from glass.pys.oss import fprop


def grsclip(inshp, clipshp, outshp, cmd=None, clip_by_region=None):
    """
    Clip Analysis using GRASS GIS
    """

    if not cmd:
        from grass.pygrass.modules import Module
        
        if not clip_by_region:
            vclip = Module(
                "v.clip", input=inshp, clip=clipshp,
                output=outshp, overwrite=True, run_=False, quiet=True
            )
        else:
            vclip = Module(
                "v.clip", input=inshp, output=outshp, overwrite=True,
                flags='r', run_=False, quiet=True
            )
        
        vclip()
    
    else:
        from glass.pys import execmd

        clipstr = f" clip={clipshp}" if clipshp else ""
        flag = "-r " if not clipshp else ""
        
        rcmd = execmd((
            f"v.clip input={inshp}{clipstr} "
            f"output={outshp} {flag}--overwrite --quiet"
        ))
    
    return outshp


def clip(inFeat, clipFeat, outFeat, api_gis="grass", clip_by_region=None):
    """
    Clip Analysis
    
    api_gis Options:
    * grass
    * pygrass
    * ogr2ogr
    """
    
    if api_gis == "pygrass" or api_gis == "grass":
        from glass.wenv.grs import run_grass
        from glass.prop.prj import get_epsg

        epsg = get_epsg(inFeat)

        work = os.path.dirname(outFeat)
        refname = fprop(outFeat, 'fn')
        loc = f"loc_{refname}"

        grsbase = run_grass(work, location=loc, srs=epsg)

        import grass.script.setup as gsetup

        gsetup.init(grsbase, work, loc, 'PERMANENT')

        from glass.it.shp import shp_to_grs, grs_to_shp

        shp = shp_to_grs(  inFeat, fprop(inFeat, 'fn'))
        clp = shp_to_grs(clipFeat, fprop(clipFeat, 'fn'))

        # Clip
        rslt = grsclip(
            shp, clp, refname,
            cmd=True if api_gis == "grass" else None,
            clip_by_region=clip_by_region
        )

        # Export
        grs_to_shp(rslt, outFeat, 'area')
    
    elif api_gis == 'ogr2ogr':
        from glass.pys    import execmd
        from glass.prop import drv_name

        rcmd = execmd((
            "ogr2ogr -f \"{}\" {} {} -clipsrc {} -clipsrclayer {}"
        ).format(
            drv_name(outFeat), outFeat, inFeat, clipFeat,
            fprop(clipFeat, 'fn')
        ))
    
    else:
        raise ValueError("{} is not available!".format(api_gis))
    
    return outFeat


def clip_shp_by_listshp(inShp, clipLst, outLst):
    """
    Clip shapes using as clipFeatures all SHP in clipShp
    Uses a very fast process with a parallel procedures approach
    
    For now, only works with GRASS GIS
    """
    
    o = [grsclip(
        inShp, clipLst[i], outLst[i], cmd=True
    ) for i in range(len(clipLst))]
    
    return outLst


def clipshp_shpinfolder(ishp, clipshps, ofolder, bname=None):
    """
    Clip Feature Class using as clip features each file of one folder
    """

    import pandas as pd

    from glass.pys.oss  import lst_ff
    from glass.prop.prj import get_epsg
    from glass.wenv.grs import run_grass

    ishpname = fprop(ishp, 'fn')
    bname = ishpname if not bname else bname

    # List clip shapes and get their id's

    # assuming file id is the last part of the filename
    # {filename}_{id}.shp
    # id must be an integer

    cshps = pd.DataFrame([{
        'fid' : int(f.split('.')[0].split('_')[-1]),
        'shp' : f
    } for f in lst_ff(
        clipshps, rfilename=True, file_format='.shp'
    )])

    # Start GRASS GIS Session
    loc = f'loc_{os.path.basename(ofolder).replace("_", "")}'
    gb = run_grass(ofolder, location=loc, srs=get_epsg(ishp))

    import grass.script.setup as gs

    gs.init(gb, ofolder, loc, 'PERMANENT')

    from glass.it.shp   import shp_to_grs, grs_to_shp
    from glass.wenv.grs import shp_to_region

    # Import in_shp
    ingrsv = shp_to_grs(ishp, ishpname)

    # Set region
    shp_to_region(ingrsv, 10)

    # Run clip
    for i, row in cshps.iterrows():
        # Import clip features
        cfeat = shp_to_grs(
            os.path.join(clipshps, row.shp),
            fprop(row.shp, 'fn'))
    
        # Clip
        clipfeat = grsclip(ingrsv, cfeat, f'{bname}_{str(row.fid)}', cmd=True)
    
        # Export
        grs_to_shp(clipfeat, os.path.join(
            ofolder, f'{clipfeat}.shp'
        ), 'area')

    return ofolder


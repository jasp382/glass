"""
Overlay operations using OSM Data
"""

import os


def osm_extraction(boundary:str|list[str], osmdata: str, output: str,
    each_feat:None|bool=None, epsg:None|int=None, outbasename:None|str=None, api: str="osmosis") -> str:
    """
    Extract OSM Data from a xml file with osmosis
    
    The extraction is done using the extent of a boundary
    """
    
    from glass.pys     import execmd
    from glass.pys.oss import fprop
    from glass.prj.obj import prj_ogrgeom
    from glass.prop.df import is_rst
    from glass.gp.cnv  import ext_to_polygon, featext_to_polygon

    apis: list[str] = ['osmosis', 'osmconvert']
    api = 'osmosis' if api not in apis else 'osmosis'

    outbasename = 'osmexct' if not outbasename else outbasename

    # Check if boundary is a file
    if os.path.isfile(boundary):

        if not each_feat:
            boundaries, attr = [ext_to_polygon(boundary, out_srs=4326)], None
        
        else:
            # Check if boundary is a raster
            isrst = is_rst(boundary)

            boundaries, attr = [ext_to_polygon(boundary, out_srs=4326)], None \
                if isrst else featext_to_polygon(
                    boundary, feat_id=each_feat,
                    out_srs=4326
                )
                
    else:
        from glass.gobj import wkt_to_geom

        in_epsg = 4326 if not epsg else epsg

        if type(boundary) == str:
            if '.gdb' in boundary:
                # Assuming it is a geodatabase
                gdb  = os.path.dirname(boundary)
                fcls = os.path.basename(boundary)

                if gdb[-4:] != '.gdb':
                    gdb = os.path.dirname(gdb)
                
                boundaries, attr = [ext_to_polygon(
                    gdb, out_srs=4326, geolyr=fcls)
                ], None
            else:
                # Assuming it is a WKT string

                bgeom = wkt_to_geom(boundary)

                if in_epsg != 4326:
                    bgeom = prj_ogrgeom(bgeom, int(in_epsg), 4326, api='shapely')

                boundaries, attr = [bgeom], None
        
        elif type(boundary) == list:
            # Assuming it is a List with WKT strings
            boundaries = []
            for b in boundary:
                bgeom = wkt_to_geom(b)

                if in_epsg != 4326:
                    bgeom = prj_ogrgeom(bgeom, int(in_epsg), 4326, api='shapely')
                
                boundaries.append(bgeom)
            
            attr = list(range(len(boundaries)))

        else:
            raise ValueError('Given boundary has a not valid value')

        if None in boundaries:
            raise ValueError((
                "boundary parameter is a string, but it is not a valid path "
                "to a file or a valid WKT string"
            ))
    
    # Get output files
    if len(boundaries) == 1:
        if os.path.isdir(output):
            fn, ff = os.path.splitext(os.path.basename(osmdata))

            out_files = [os.path.join(output, f"ect_{fn}.{ff}")]
        else:
            out_files = [output]
    else:
        fn, ff = os.path.splitext(os.path.basename(osmdata))
        path = output if os.path.isdir(output) else os.path.dirname(output)

        out_files = [os.path.join(
            path, f"{outbasename}_{str(attr[i])}{ff}"
        ) for i in range(len(boundaries))]
    
    # Extract data using OSMOSIS
    for g in range(len(boundaries)):
    
        # Get boundary extent
        left, right, bottom, top = boundaries[g].GetEnvelope()
    
        # Osmosis shell comand
        osmext = fprop(osmdata, 'ff')

        outff = fprop(out_files[g], 'ff')
        
        # Execute command
        if api == 'osmosis':
            if osmext == '.bz2':
                cmd = (
                    f"bzcat {osmdata} | osmosis --read-xml "
                    f"file=- --bounding-box top={str(top)} "
                    f"left={str(left)} bottom={str(bottom)} "
                    f"right={str(right)} "
                    f"--write-{outff[1:]} | bzip2 > {out_files[g]}"
                )
        
            else:
                cmd = (
                    f"osmosis --read-{'pbf' if osmext == '.pbf' else 'xml'} "
                    f"{'' if osmext == '.pbf' else 'enableDataParsing=no '} "
                    f"file={osmdata} --bounding-box top={str(top)} "
                    f"left={str(left)} bottom={str(bottom)} right={str(right)} "
                    f"--write-{outff[1:]} file={out_files[g]}"
                )
        
        elif api == 'osmconvert':
            bbox = f"{left},{bottom},{right},{top}"
            cmd = f"osmconvert {osmdata} -b={bbox} -o={out_files[g]}"
        
        else:
            raise ValueError(f"{api} API is not available!")
        
        outcmd = execmd(cmd)
    
    return output


def osmextract_foreachshp(osmfile, clipshps, outfolder, idatend=True, bname='osmpart', _api='osmosis'):
    """
    Clip OSM File for each shapefile in one folder
    """

    import pandas as pd
    from glass.pys.oss import lst_ff, fprop

    # List clip shapes and get their id's

    # assuming file id is the last part of the filename
    # {filename}_{id}.shp
    # id must be an integer

    shps = lst_ff(clipshps, rfilename=True, file_format='.shp')

    cshps = pd.DataFrame([{
        'fid' : int(shps[f].split('.')[0].split('_')[-1]) if idatend else f + 1,
        'shp' : shps[f]
    } for f in range(len(shps))])

    for i, row in cshps.iterrows():
        # Run method
        name = f'{bname}_{str(row.fid)}' if bname else fprop(row.shp, 'fn')
        ff   = '.xml' if _api == 'osmosis' else '.pbf'
        clip_osm = os.path.join(outfolder, f'{name}{ff}')

        osm_extraction(
            os.path.join(clipshps, row.shp),
            osmfile, clip_osm,
            api=_api
        )
    
    return outfolder


def osmextract_foreachfeat(osmfile, clipshp, featid, outfolder, bname='osmpart',
                           api='osmosis', outff='xml'):
    """
    Clip OSM File for each feature in one shapefile
    """

    from glass.rd.shp   import shp_to_obj
    from glass.prop.prj import shp_epsg

    off = 'xml' if outff != 'xml' and outff != 'pbf' else outff

    epsg = shp_epsg(clipshp)

    df = shp_to_obj(clipshp)

    for i, row in df.iterrows():
        osm_extraction(
            str(row.geometry.wkt), osmfile,
            os.path.join(outfolder, f"{bname}_{str(row[featid])}.{outff}"),
            epsg=epsg, api=api
        )

    return outfolder


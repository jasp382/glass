"""
Overlay operations using OSM Data
"""

import os


def osm_extraction(boundary, osmdata: str, output: str,
    each_feat=None, epsg=None, outbasename=None, api="osmosis"):
    """
    Extract OSM Data from a xml file with osmosis
    
    The extraction is done using the extent of a boundary
    """
    
    from glass.pys     import execmd
    from glass.pys.oss import fprop
    from glass.prj.obj import prj_ogrgeom
    from glass.prop.df import is_rst

    apis = ['osmosis', 'osmconvert']
    api = 'osmosis' if api not in apis else 'osmosis'

    refattr = []
    outbasename = 'osmexct' if not outbasename else outbasename

    # Check if boundary is a file
    if os.path.isfile(boundary):
        # Check if boundary is a raster
        isrst = is_rst(boundary)

        if isrst:
            # Get Raster EPSG and Extent
            from glass.prop.prj import rst_epsg
            from glass.prop.rst import rst_ext
            from glass.gobj     import create_polygon

            in_epsg = rst_epsg(boundary)
            left, right, bottom, top = rst_ext(boundary)
            boundaries = [create_polygon([
                (left, top), (right, top), (right, bottom),
                (left, bottom), (left, top)
            ])]
        
    
        else:
            # Get Shape EPSG
            from glass.prop.prj import shp_epsg

            in_epsg = shp_epsg(boundary)

            if not each_feat:
                # Get Shape Extent
                from glass.prop.feat import get_ext
                from glass.gobj      import create_polygon

                left, right, bottom, top = get_ext(boundary)
                boundaries = [create_polygon([
                    (left, top), (right, top), (right, bottom),
                    (left, bottom), (left, top)
                ])]
        
            else:
                # Get Extent of each feature
                from osgeo         import ogr
                from glass.prop.df import drv_name

                src = ogr.GetDriverByName(drv_name(boundary)).Open(boundary)
                lyr = src.GetLayer()

                boundaries = []

                for feat in lyr:
                    boundaries.append(feat.GetGeometryRef())
                    refattr.append(feat.GetField(each_feat) \
                        if type(each_feat) == str else feat.GetFID())
                
    else:
        from glass.gobj import wkt_to_geom

        in_epsg = 4326 if not epsg else epsg

        if type(boundary) == str:
            # Assuming it is a WKT string
            wkt_boundaries = [boundary]
        elif type(boundary) == list:
            # Assuming it is a List with WKT strings
            wkt_boundaries = boundary
        else:
            raise ValueError(
                'Given boundary has a not valid value'
            )
        
        boundaries = [wkt_to_geom(g) for g in wkt_boundaries]
        refattr = list(range(len(boundaries)))

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
            path, f"{outbasename}_{str(refattr[i])}{ff}"
        ) for i in range(len(boundaries))]
    
    # Extract data using OSMOSIS
    for g in range(len(boundaries)):
        # Convert boundary to WGS84 -EPSG 4326
        geom_wgs = prj_ogrgeom(
            boundaries[g], int(in_epsg), 4326, api='shapely'
        ) if int(in_epsg) != 4326 else boundaries[g]
    
        # Get boundary extent
        left, right, bottom, top = geom_wgs.GetEnvelope()
    
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


def osmextract_foreachshp(osmfile, clipshps, outfolder, bname='osmpart'):
    """
    Clip OSM File for each shapefile in one folder
    """

    import pandas as pd
    from glass.pys.oss import lst_ff

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

    for i, row in cshps.iterrows():
        # Run method
        osm_extraction(
            os.path.join(clipshps, row.shp),
            osmfile,
            os.path.join(outfolder, f'{bname}_{str(row.fid)}.xml')
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


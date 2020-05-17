"""
Overlay operations using OSM Data
"""

import os


def osm_extraction(boundary, osmdata: str, output: str,
    each_feat=None, epsg=None, outbasename=None):
    """
    Extract OSM Data from a xml file with osmosis
    
    The extraction is done using the extent of a boundary
    """
    
    from glass.pys       import execmd
    from glass.prj.obj import prj_ogrgeom
    from glass.prop    import check_isRaster

    refattr = []
    outbasename = 'osmexct' if not outbasename else outbasename

    # Check if boundary is a file
    if os.path.isfile(boundary):
        # Check if boundary is a raster
        is_rst = check_isRaster(boundary)

        if is_rst:
            # Get Raster EPSG and Extent
            from glass.prop.prj import get_rst_epsg
            from glass.prop.rst import rst_ext
            from glass.gobj     import create_polygon

            in_epsg = get_rst_epsg(boundary)
            left, right, bottom, top = rst_ext(boundary)
            boundaries = [create_polygon([
                (left, top), (right, top), (right, bottom),
                (left, bottom), (left, top)
            ])]
        
    
        else:
            # Get Shape EPSG
            from glass.prop.prj import get_shp_epsg

            in_epsg = get_shp_epsg(boundary)

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
                from osgeo        import ogr
                from glass.prop import drv_name

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
            path, f"{outbasename}_{str(refattr[i])}.xml"
        ) for i in range(len(boundaries))]
    
    # Extract data using OSMOSIS
    cmd = (
        "osmosis --read-{_f} {dtparse}file={_in} "
        "--bounding-box top={t} left={l} bottom={b} right={r} "
        "--write-{outext} file={_out}"
    )
    for g in range(len(boundaries)):
        # Convert boundary to WGS84 -EPSG 4326
        geom_wgs = prj_ogrgeom(
            boundaries[g], int(in_epsg), 4326, api='shapely'
        ) if int(in_epsg) != 4326 else boundaries[g]
    
        # Get boundary extent
        left, right, bottom, top = geom_wgs.GetEnvelope()
    
        # Osmosis shell comand
        osmext = os.path.splitext(osmdata)[1]
        
        # Execute command
        outcmd = execmd(cmd.format(
            _f='pbf' if osmext == '.pbf' else 'xml', _in=osmdata,
            t=str(top), l=str(left), b=str(bottom), r=str(right),
            _out=out_files[g], outext=os.path.splitext(out_files[g])[1][1:],
            dtparse="" if osmext == '.pbf' else "enableDataParsing=no "
        ))
    
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


def osmextract_foreachfeat(osmfile, clipshp, featid, outfolder, bname='osmpart'):
    """
    Clip OSM File for each feature in one shapefile
    """

    from glass.rd.shp   import shp_to_obj
    from glass.prop.prj import get_shp_epsg

    epsg = get_shp_epsg(clipshp)

    df = shp_to_obj(clipshp)

    for i, row in df.iterrows():
        osm_extraction(
            str(row.geometry.wkt), osmfile,
            os.path.join(outfolder, f"{bname}_{str(row[featid])}.xml"),
            epsg=epsg
        )

    return outfolder


"""
Bufering TOOLS
"""

"""
Memory Based
"""


def _buffer(inShp, radius, outShp,
            api='geopandas', dissolve=None, geom_type=None,
            lyrn=1):
    """
    Buffering on Shapefile
    
    API's Available
    * geopandas;
    * saga;
    * grass;
    * pygrass;
    """
    
    if api == 'geopandas':
        from glass.rd.shp            import shp_to_obj
        from glass.gp.prox.bfing.obj import geodf_buffer_to_shp
    
        geoDf_ = shp_to_obj(inShp)
    
        geodf_buffer_to_shp(geoDf_, radius, outShp)
    
    elif api == 'saga':
        """
        A vector based buffer construction partly based on the method supposed by
        Dong et al. 2003. 
        """
        
        from glass.pys import execmd
        
        distIsField = True if type(radius) == str else None
        distOption  = "-DIST_FIELD_DEFAULT" if not distIsField else \
            "-DIST_FIELD"
        
        diss="0" if not dissolve else "1"
        
        outcmd = execmd((
            f"saga_cmd shapes_tools 18 -SHAPES {inShp} "
            f"-BUFFER {outShp} {distOption} "
            f"{str(radius)} -DISSOLVE {diss}"
        ))
    
    elif api=='pygrass':
        from grass.pygrass.modules import Module
        
        if not geom_type:
            raise ValueError((
                'geom_type parameter must have a value when using '
                'pygrass API'
            ))
        
        _flags = 't' if not dissolve else ''
        lyrn = 1 if not lyrn else lyrn
        
        bf = Module(
            "v.buffer", input=inShp, type=geom_type,
            distance=radius if type(radius) != str else None,
            column=radius if type(radius) == str else None,
            flags=_flags, output=outShp, layer=lyrn,
            overwrite=True, run_=False, quiet=True
        )
        
        bf()
    
    elif api == 'grass':
        from glass.pys import execmd

        lyrn = "1" if not lyrn else str(lyrn)

        pdist = "column" if type(radius) == str else "distance"
        _t = '' if dissolve else ' -t'
        
        rcmd = execmd((
            f"v.buffer input={inShp} type={geom_type} "
            f"layer={lyrn} {pdist}={str(radius)} "
            f"output={outShp}{_t} --overwrite --quiet"
        ))
    
    else:
        raise ValueError(f"{api} is not available!")
    
    return outShp


"""
Buffers based on extent
"""

def buffer_ext(inShp, meterTolerance, outShp, inEpsg=None):
    """
    For all geometries, calculate the boundary given by 
    the sum between the feature extent and the Tolerance variable
    """
    
    from glass.rd.shp            import shp_to_obj
    from glass.wt.shp            import df_to_shp
    from glass.gp.prox.bfing.obj import df_buffer_extent
    from glass.prop.prj          import get_shp_epsg
    
    inDf = shp_to_obj(inShp)

    epsg = get_shp_epsg(inShp) if not inEpsg else inEpsg
    
    result = df_buffer_extent(inDf, epsg, meterTolerance)
    
    return df_to_shp(result, outShp)


def buffer_shpFolder(inFolder, outFolder, dist_or_field, fc_format='.shp',
                     __api='ogr'):
    """
    Create buffer polygons for all shp in one folder
    """
    
    import os; from glass.pys.oss import lst_ff
    
    lst_fc = lst_ff(inFolder, file_format=fc_format)
    
    for fc in lst_fc:
        _buffer(
            fc, dist_or_field, os.path.join(outFolder, os.path.basename(fc)),
            api=__api 
        )


def dic_buffer_array_to_shp(arrayBf, outShp, epsg, fields=None):
    """
    Array with dict with buffer proprieties to Feature Class
    """
    
    import os; from osgeo        import ogr
    from glass.prop              import drv_name
    from glass.prop.prj          import get_sref_from_epsg
    from glass.gp.prox.bfing.obj import xy_to_buffer
    
    # Get SRS for output
    srs = get_sref_from_epsg(epsg)
    
    # Create output DataSource and Layer
    outData = ogr.GetDriverByName(
        drv_name(outShp)).CreateDataSource(outShp)
    
    lyr = outData.CreateLayer(
        os.path.splitext(os.path.basename(outShp))[0],
        srs, geom_type=ogr.wkbPolygon
    )
    
    # Create fields
    if fields:
        from glass.lyr.fld import fields_to_lyr
        
        fields_to_lyr(lyr, fields)
    
    lyrDefn = lyr.GetLayerDefn()
    for _buffer in arrayBf:
        newFeat = ogr.Feature(lyrDefn)
        
        geom = xy_to_buffer(_buffer["X"], _buffer["Y"], _buffer["RADIUS"])
        
        newFeat.SetGeometry(geom)
        
        for field in fields:
            if field in _buffer.keys():
                newFeat.SetField(field, _buffer[field])
        
        lyr.CreateFeature(newFeat)
        
        newFeat.Destroy()
    
    del lyrDefn
    outData.Destroy()
    
    return outShp


def get_sub_buffers(x, y, radius):
    """
    Get Smaller Buffers for each cardeal point (North,
    South, East, West, Northeast, Northwest,
    Southwest and Southeast)
    """
    
    sub_buf = ['north', 'northeast', 'east', 'southeast',
               'south', 'southwest', 'west', 'northwest']
    
    lstSubBuffer = []
    
    for cardeal in sub_buf:
        if cardeal == 'north':
            _y = y + (radius / 2)
        
        elif cardeal == 'northeast' or cardeal == 'northwest':
            _y =  y + ((radius)**2 / 8.0)**0.5
        
        elif cardeal == 'south':
            _y = y - (radius / 2)
        
        elif cardeal == 'southwest' or cardeal == 'southeast':
            _y = y - ((radius)**2 / 8.0)**0.5
        
        else:
            _y = y
        
        if cardeal == 'west':
            _x = x - (radius / 2)
        
        elif cardeal == 'southwest' or cardeal == 'northwest':
            _x = x - ((radius)**2 / 8.0)**0.5
        
        elif cardeal == 'east':
            _x = x + (radius / 2)
        
        elif cardeal == 'southeast' or cardeal == 'northeast':
            _x = x + ((radius)**2 / 8.0)**0.5
        
        else:
            _x = x
        
        lstSubBuffer.append({
            'X' : _x, 'Y' : _y,
            'RADIUS' : radius / 2,
            'cardeal' : cardeal
        })
    
    return lstSubBuffer



def cheese_buffer(inshp, dist, angles_int, outshp,
                    epsg=None, regbuffer=None, precheese=None,
                    uniqueid='sliceid', areaf=None, shpid=None):
    """
    Create a buffer in all directions
    """

    import numpy                 as np
    import geopandas             as gp
    from glass.gp.prox.bfing.obj import geodf_buffer
    from glass.gobj              import create_polygon
    from glass.rd.shp            import shp_to_obj
    from glass.wt.shp            import df_to_shp
    from glass.pd.dagg           import col_listwlist_to_row
    from glass.dtr.mge.pd        import merge_df
    from glass.it.pd             import df_to_geodf

    if not epsg:
        from glass.prop.prj import get_epsg

        epsg = get_epsg(inshp)


    def run_cheese_buffer(r, _featid):
        multipoly = []
    
        minangle = 0
        maxangle = angles_int
    
        while maxangle <= 360:
            coords = [(r.x, r.y)]
            for i in range(minangle, maxangle + 1):
                y = r.y + ((r.dist + dist) * np.cos(np.radians(i)))
                x = r.x + ((r.dist + dist) * np.sin(np.radians(i)))
    
                coords.append((x, y))
        
            coords.append((r.x, r.y))   
    
            poly = create_polygon(coords, api='shapely')
        
            multipoly.append([r[_featid], poly, f"{str(minangle)}-{str(maxangle)}"])
        
            minangle += angles_int
            maxangle += angles_int
    
        r["geoms"] = multipoly
    
        return r
    
    featid = 'featid' if not shpid else shpid
    
    pdf = shp_to_obj(inshp)

    # Get Regular Buffer
    rbf = geodf_buffer(pdf, dist)

    if not shpid:
        rbf['ofeatid'] = rbf.index
    
    else:
        rbf.rename(columns={shpid: 'ofeatid'}, inplace=True)

    # Save original polygons
    odf = pdf.copy()

    # Get Cheese buffer
    s = pdf.geometry

    t = gp.GeoSeries(gp.points_from_xy(
        s.envelope.bounds.maxx,
        s.envelope.bounds.maxy
    ), crs=epsg)

    pdf["dist"] = s.envelope.centroid.distance(t)

    pdf['x'] = s.envelope.centroid.x
    pdf['y'] = s.envelope.centroid.y

    if not shpid:
        pdf[featid] = pdf.index

    pdf = pdf.apply(lambda x: run_cheese_buffer(x, featid), axis=1)

    pdf.drop(["x", "y", "geometry"], axis=1, inplace=True)

    pdf = col_listwlist_to_row(
        pdf, "geoms", ["ofid", "geom", "direction"],
        geomcol="geom", epsg=epsg
    )

    # Save regular buffer
    if regbuffer:
        df_to_shp(rbf, regbuffer)

    # Save pre-cheese buffer
    if precheese:
        df_to_shp(pdf, precheese)
    
    # Get final buffer 
    # by intersecting pre-cheese and regular buffer
    dfs = []
    for i, row in odf.iterrows():
        # Get slices
        slices = pdf[pdf.ofid == i]
    
        # Get regular buffer
        regbf = rbf[rbf.ofeatid == i]
        regbf = regbf.to_dict(orient="records")
    
        bfgeom = regbf[0]["geometry"]
    
        # Get Intersection
        slices["geometry"] = slices.geom.intersection(bfgeom)
    
        dfs.append(slices)
    
    # Merge all dataframes
    fdf = merge_df(dfs)
    fdf = df_to_geodf(fdf, 'geometry', epsg)

    # Remove features with area == 0
    fdf = fdf[fdf.geometry.area > 0]

    fdf.reset_index(inplace=True)

    fdf.drop(['geom', 'ofid'], axis=1, inplace=True)

    # Get Features UNIQUE IDENTIFIER
    if uniqueid:
        fdf[uniqueid] = fdf[featid] + '__' + fdf['direction']

    # Return Area in SQUARE METERS
    if areaf:
        fdf[areaf] = fdf.geometry.area

    df_to_shp(fdf, outshp)

    return outshp


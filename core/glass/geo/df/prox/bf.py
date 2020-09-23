"""
Bufering TOOLS
"""

"""
Memory Based
"""

def geoseries_buffer(gseries, dist):
    """
    Buffer of GeoSeries
    """
    
    return gseries.buffer(dist, resolution=16)


def geodf_buffer_to_shp(geoDf, dist, outfile, colgeom='geometry'):
    """
    Execute the Buffer Function of GeoPandas and export
    the result to a new shp
    """
    
    from glass.dct.geo.toshp import df_to_shp
    
    __geoDf = geoDf.copy()
    __geoDf["buffer_geom"] = __geoDf[colgeom].buffer(dist, resolution=16)
    
    __geoDf.drop(colgeom, axis=1, inplace=True)
    __geoDf.rename(columns={"buffer_geom" : colgeom}, inplace=True)
    
    df_to_shp(__geoDf, outfile)
    
    return outfile


def ogr_buffer(geom, radius, out_file, srs=None):
    """
    For each geometry in the input, this method create a buffer and store it
    in a vetorial file
    
    Accepts files or lists with geom objects as inputs
    """
    
    import os
    from osgeo            import ogr
    from glass.geo.df.prj      import def_prj
    from glass.geo.prop.df  import drv_name
    from glass.geo.prop.prj import get_sref_from_epsg
    from glass.geo.obj.gop.prox  import draw_buffer
    
    # Create output
    buffer_shp = ogr.GetDriverByName(
        drv_name(out_file)).CreateDataSource(out_file)
    
    buffer_lyr = buffer_shp.CreateLayer(
        os.path.splitext(os.path.basename(out_file))[0],
        get_sref_from_epsg(srs) if srs else None,
        geom_type=ogr.wkbPolygon
    )
    
    featDefn = buffer_lyr.GetLayerDefn()
    
    if type(geom) == list:
        for g in geom:
            feat = ogr.Feature(featDefn)
            feat.SetGeometry(draw_buffer(g, radius))
            
            buffer_lyr.CreateFeature(feat)
            
            feat = None
        
        buffer_shp.Destroy()
    
    elif type(geom) == dict:
        if 'x' in geom and 'y' in geom:
            X='x'; Y='y'
        elif 'X' in geom and 'Y' in geom:
            X='X'; Y='Y'
        else:
            raise ValueError((
                'Your geom dict has invalid keys. '
                'Please use one of the following combinations: '
                'x, y; '
                'X, Y'
            ))
        
        from glass.geo.obj.g import new_pnt
        
        feat = ogr.Feature(featDefn)
        g = new_pnt(geom[X], geom[Y])
        feat.SetGeometry(draw_buffer(g, radius))
        
        buffer_lyr.CreateFeature(feat)
        
        feat = None
        
        buffer_shp.Destroy()
        
        if srs:
            def_prj(out_file, epsg=srs)
    
    elif type(geom) == str:
        # Check if the input is a file
        if os.path.exists(geom):
            inShp = ogr.GetDriverByName(drv_name(geom)).Open(geom, 0)
            
            lyr = inShp.GetLayer()
            for f in lyr:
                g = f.GetGeometryRef()
                
                feat = ogr.Feature(featDefn)
                feat.SetGeometry(draw_buffer(g, radius))
                
                buffer_lyr.CreateFeature(feat)
                
                feat = None
            
            buffer_shp.Destroy()
            inShp.Destroy()
            
            if srs:
                def_prj(out_file, epsg=srs)
            else:
                def_prj(out_file, template=geom)
            
        else:
            raise ValueError('The given path does not exist')
    
    else:
        raise ValueError('Your geom input is not valid')
    
    return out_file


def _buffer(inShp, radius, outShp,
            api='geopandas', dissolve=None, geom_type=None):
    """
    Buffering on Shapefile
    
    API's Available
    * geopandas;
    * saga;
    * grass;
    * pygrass;
    """
    
    if api == 'geopandas':
        from glass.dct.geo.fmshp import shp_to_obj
    
        geoDf_ = shp_to_obj(inShp)
    
        geodf_buffer_to_shp(geoDf_, radius, outShp)
    
    elif api == 'saga':
        """
        A vector based buffer construction partly based on the method supposed by
        Dong et al. 2003. 
        """
        
        from glass.pys import execmd
        
        distIsField = True if type(radius) == str else None
        
        c = (
            "saga_cmd shapes_tools 18 -SHAPES {_in} "
            "-BUFFER {_out} {distOption} {d} -DISSOLVE {diss}"
        ).format(
            _in=inShp,
            distOption = "-DIST_FIELD_DEFAULT" if not distIsField else \
                "-DIST_FIELD",
            d=str(radius),
            _out=outShp,
            diss="0" if not dissolve else "1"
        )
        
        outcmd = execmd(c)
    
    elif api=='pygrass':
        from grass.pygrass.modules import Module
        
        if not geom_type:
            raise ValueError((
                'geom_type parameter must have a value when using '
                'pygrass API'
            ))
        
        bf = Module(
            "v.buffer", input=inShp, type=geom_type,
            distance=radius if type(radius) != str else None,
            column=radius if type(radius) == str else None,
            flags='t', output=outShp,
            overwrite=True, run_=False, quiet=True
        )
        
        bf()
    
    elif api == 'grass':
        from glass.pys import execmd
        
        rcmd = execmd((
            "v.buffer input={} type={} layer=1 {}={} "
            "output={} -t --overwrite --quiet"
        ).format(
            inShp, geom_type,
            "column" if type(radius) == str else "distance",
            str(radius), outShp
        ))
    
    else:
        raise ValueError("{} is not available!".format(api))
    
    return outShp


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
    
    import os; from osgeo      import ogr
    from glass.geo.prop.df  import drv_name
    from glass.geo.prop.prj import get_sref_from_epsg
    from glass.geo.obj.gop.prox import xy_to_buffer
    
    # Get SRS for output
    srs = get_sref_from_epsg(epsg)
    
    # Create output DataSource and Layer
    outData = ogr.GetDriverByName(drv_name(outShp)).CreateDataSource(outShp)
    
    lyr = outData.CreateLayer(
        os.path.splitext(os.path.basename(outShp))[0],
        srs, geom_type=ogr.wkbPolygon
    )
    
    # Create fields
    if fields:
        from glass.geo.obj.lyr.fld import fields_to_lyr
        
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


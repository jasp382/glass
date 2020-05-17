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
        
        rcmd = execmd((
            "v.buffer input={} type={} layer=1 {}={} "
            "output={}{} --overwrite --quiet"
        ).format(
            inShp, geom_type,
            "column" if type(radius) == str else "distance",
            str(radius), outShp,
            '' if dissolve else ' -t'
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
    
    import os; from osgeo          import ogr
    from glass.prop              import drv_name
    from glass.prop.prj          import get_sref_from_epsg
    from glass.gp.prox.bfing.obj import xy_to_buffer
    
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


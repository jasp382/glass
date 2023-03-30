"""
Tools for Geometric Generalization
"""

def df_dissolve(df, field):
    """
    Dissolve using GeoPandas
    """

    dissDf = df.dissolve(by=field)

    return dissDf


def dissolve(inShp, outShp, fld,
             statistics=None, api='ogr', inputIsLines=None):
    """
    Dissolve Geometries
    
    API's Available:
    * qgis;
    * saga;
    * ogr;
    * pygrass;
    * grass;
    """
    
    if api == 'qgis':
        import processing
        
        processing.runalg("qgis:dissolve", inShp, False, fld, outShp)
    
    elif api == 'saga':
        """
        Dissolve vectorial data by field
    
        This algorithm doesn't allow self intersections
        """
        
        from glass.pys  import execmd
        
        if not inputIsLines:
            cmd = (
                f'saga_cmd shapes_polygons 5 -POLYGONS {inShp} -FIELDS {fld} '
                f'-DISSOLVED {outShp}'
            )
        
        else:
            cmd = (
                f'saga_cmd shapes_lines 5 -LINES {inShp} -FIELD_1 '
                f'{fld} -DISSOLVED {outShp} -ALL 0'
            )
        
        outcmd = execmd(cmd)
    
    elif api == 'ogr':
        """
        Dissolve with OGR and sqlite sql
    
        field_statitics used to preserve numeric fields aggregating their values
        using some statistics
        field_statistics = {fld_name: SUM, fld_name: AVG}
    
        TODO: DISSOLVE WITHOUT FIELD
        """
        
        from glass.pys     import execmd
        from glass.pys.oss import fprop

        tname = fprop(inShp, 'fn')

        stat = '' if not statistics else ', ' + ','.join([
            f'{statistics[fld]}({fld}) AS {fld}' for fld in statistics
        ])

        q = (
            f'SELECT {fld}{stat}, ST_Union(geometry) '
            f'FROM {tname} '
            f'GROUP BY {fld}'
        )
        
        cmd = (
            f'ogr2ogr {outShp} {inShp} -dialect '
            f'sqlite -sql "{q};"'
        )
        
        # Execute command
        outcmd = execmd(cmd)
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module
        
        diss = Module(
            "v.dissolve", input=inShp, column=fld, output=outShp,
            overwrite=True, run_=False, quiet=True
        )
        
        diss()
    
    elif api == 'grass':
        from glass.pys  import execmd
        
        outCmd = execmd((
            f"v.dissolve input={inShp} "
            f"{f'column={fld} ' if fld else ''}"
            f"output={outShp} --overwrite --quiet"
        ))
    
    elif api == 'pandas':
        from glass.rd.shp import shp_to_obj
        from glass.wt.shp import df_to_shp

        gdf = shp_to_obj(inShp)

        ndf = df_dissolve(gdf, fld)

        outshp = df_to_shp(ndf, outShp)
    
    else:
        raise ValueError(f'The api {api} is not available')
    
    return outShp


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
             statistics=None, geomMultiPart=True, api='ogr', inputIsLines=None):
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
                'saga_cmd shapes_polygons 5 -POLYGONS {in_poly} -FIELDS {fld} '
                '-DISSOLVED {out_shp}'
            ).format(
                in_poly=inShp, fld=fld, out_shp=outShp
            )
        
        else:
            cmd = (
                'saga_cmd shapes_lines 5 -LINES {} -FIELD_1 {} -DISSOLVED {} '
                '-ALL 0'
            ).format(inShp, fld, outShp)
        
        outcmd = execmd(cmd)
    
    elif api == 'ogr':
        """
        Dissolve with OGR and sqlite sql
    
        field_statitics used to preserve numeric fields aggregating their values
        using some statistics
        field_statistics = {fld_name: SUM, fld_name: AVG}
    
        TODO: DISSOLVE WITHOUT FIELD
        """
        
        import os
        from glass.pys      import execmd
        from glass.pys .oss import fprop
        
        if not statistics:
            cmd = (
                'ogr2ogr {o} {i} -dialect sqlite -sql '
                '"SELECT ST_Union(geometry), {f} '
                'FROM {t} GROUP BY {f};"'
            ).format(o=outShp, i=inShp, f=fld, t=fprop(shp, 'fn'))
        
        else:
            cmd = (
                'ogr2ogr {o} {i} -dialect sqlite -sql '
                '"SELECT ST_Union(geometry), {f}, {stat} '
                'FROM {t} GROUP BY {f};"'
            ).format(
                o=outShp, i=inShp, f=fld,
                t=fprop(shp, 'fn'),
                stat=','.join([
                    '{s}({f}) AS {f}'.format(
                        f=str(fld),
                        s=statistics[fld]
                    ) for fld in statistics]
                )
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
            "v.dissolve input={}{} output={} "
             "--overwrite --quiet"
        ).format(inShp, " column={}".format(fld) if fld else "", outShp))
    
    elif api == 'pandas':
        from glass.g.rd.shp import shp_to_obj
        from glass.g.wt.shp import df_to_shp

        gdf = shp_to_obj(inShp)

        ndf = df_dissolve(gdf, fld)

        outshp = df_to_shp(ndf, outShp)
    
    else:
        raise ValueError('The api {} is not available'.format(api))
    
    return outShp


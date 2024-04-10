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
             statistics=None, api='ogr',
             ilyrname=None, olyrname=None):
    """
    Dissolve Geometries
    
    API's Available:
    * qgis;
    * saga;
    * ogr;
    * pygrass;
    * grass;
    """

    from glass.pys import obj_to_lst
    
    if api == 'qgis':
        import processing
        
        processing.runalg("qgis:dissolve", inShp, False, fld, outShp)
    
    elif api == 'saga':
        """
        Dissolve vectorial data by field
    
        This algorithm doesn't allow self intersections
        """
        
        from glass.pys import execmd
        from glass.prop.feat import get_gtype

        gt = get_gtype(inShp, gisApi='pandas')

        ilines = True if gt == 'LineString' or gt == 'MultiLineString' \
            else None
        
        cmd = (
            f'saga_cmd shapes_polygons 5 -POLYGONS {inShp} -FIELDS {fld} '
            f'-DISSOLVED {outShp}'
        ) if not ilines else (
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
        
        import os
        from glass.prop.df import drv_name
        from glass.pys     import execmd
        from glass.pys.oss import fprop

        idrv, odrv = drv_name(inShp), drv_name(outShp)

        tname = ilyrname if ilyrname and idrv == 'GPKG' \
            else fprop(inShp, 'fn')
        
        up = "-update -append " if odrv == 'GPKG' and os.path.exists(outShp) \
            else ""
        
        nln = f' -nln {olyrname}' if olyrname and idrv == 'GPKG' else ""

        stat = '' if not statistics else ', ' + ','.join([
            f'{statistics[fld]}({fld}) AS {fld}' for fld in statistics
        ])

        fld = ", ".join(obj_to_lst(fld))

        q = (
            f'SELECT {fld}{stat}, ST_Union(geometry) '
            f'FROM {tname} '
            f'GROUP BY {fld}'
        )
        
        cmd = (
            f'ogr2ogr -f "{odrv}" {up}{outShp}{nln} {inShp} '
            f'-dialect sqlite -sql "{q};"'
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



def diss_adjacent(shp, col, value, dissolve_type, out):
    """
    Dissolve adjancent polygons

    dissolve_type options:
    0 - Largest adjacent polygon;
    1 - Smallest adjacent polygon;
    2 - Largest common boundary'

    Dependencies:
    * QGIS
    """

    from qgis import processing

    from glass.rd.shp import shp_to_qgslyr

    doptions = [0, 1, 2]

    dtype = 0 if dissolve_type not in doptions else dissolve_type

    ilyr = shp_to_qgslyr(shp)

    # Select by attributes
    sp = {
        "FIELD"    : col,
        "INPUT"    : ilyr,
        'METHOD'   : 0,
        "OPERATOR" : 5,
        "VALUE"    : value
    }

    sel_lyr = processing.run('qgis:selectbyattribute', sp)

    # Dissolve
    dp = {
        'INPUT'  : sel_lyr['OUTPUT'],
        'MODE'   : dtype,
        'OUTPUT' : out
    }

    processing.run('qgis:eliminateselectedpolygons', dp)

    return out


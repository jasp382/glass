"""
Shape To some Python Object
"""

import os
import unicodedata

from glass.prop.df import lst_layers

def normalizar_string(texto):
    """Remove acentos e força minúsculas para comparação segura."""
    if not isinstance(texto, str):
        texto = str(texto)
    # Transforma "Rede Viária" em "rede viaria"
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()


def shp_to_obj(shp, geom_col=None, fields=None, output='df', srs_to=None,
    colsAsArray=None, geom_as_wkt=None, lyr=None, outgeom=None, force2D=None, organize_polygons=None):
    """
    Feature Class to Python Object

    output Options:
    - df;
    - dict;
    - array;

    organize_polygons: 'SKIP', 'ONLY_CCW' ou None
    """

    import geopandas as gp
    from glass.prop.prj import df_epsg

    if organize_polygons:
        os.environ['OGR_ORGANIZE_POLYGONS'] = organize_polygons

    if '.gdb' in shp and not lyr:
        lyr = os.path.basename(shp)
        shp = os.path.dirname(shp)

        if shp[-4:] != '.gdb':
            shp = os.path.dirname(shp)

    if not lyr:
        df = gp.read_file(shp, engine="pyogrio")
    else:
        lyrs = lst_layers(shp)

        lyr_alvo = None
        lyrnorm = normalizar_string(lyr)

        for lyr_real in lyrs:
            if normalizar_string(lyr_real) == lyrnorm:
                lyr_alvo = lyr_real
        
        if lyr_alvo is None:
            lyr_alvo = lyr

        df = gp.read_file(shp, layer=lyr_alvo, engine="pyogrio")

    # Get name of geometry col
    if not geom_col:
        for c in df.columns.values:
            if c == 'geometry' or c == 'geom':
                geom_col = c
                break
    
    if force2D:
        df[geom_col] = df[geom_col].force_2d()
    
    epsg = df_epsg(df, geom_col) if srs_to else None
    
    # Get Fields to Mantain
    if fields:
        from glass.pd.cols import del_cols_notin_ref

        df = del_cols_notin_ref(df, fields, geomCol=geom_col)
    
    # Project if necessary
    if srs_to != epsg and type(srs_to) == int:
        from glass.prj.obj import df_prj

        df = df_prj(df, srs_to)
    
    if outgeom:
        df.rename(columns={geom_col : outgeom}, inplace=True)
    
    # Produce output
    if output != 'df':

        df.rename(columns={geom_col: "GEOM"}, inplace=True)

        if geom_as_wkt:
            df["GEOM"] = df.GEOM.astype(str)

        if output == 'dict':
            orientation = "index" if not colsAsArray else "list"
        elif output == 'array':
            df["FID"] = df.index

            orientation = "records"
        
        else:
            orientation = 'dict'
        
        data = df.to_dict(orient=orientation)

        return data
    else:
        return df


def points_to_list(pntShp, listVal='tuple', inEpsg=None, outEpsg=None):
    """
    Return a list as:
    
    if listVal == 'tuple'
    l = [(x_coord, y_coord), ..., (x_coord, y_coord)]
    
    elif listVal == 'dict'
    l = [
        {id : fid_value, x : x_coord, y : y_coord},
        ...
        {id : fid_value, x : x_coord, y : y_coord}
    ]
    """
    
    geoDf = shp_to_obj(pntShp)
    
    if inEpsg and outEpsg and inEpsg != outEpsg:
        from glass.prj.obj import df_prj
        
        geoDf = df_prj(geoDf, outEpsg)
    
    geoDf["x"] = geoDf.geometry.x.astype(float)
    geoDf["y"] = geoDf.geometry.y.astype(float)
    
    if listVal == 'tuple':
        subset = geoDf[['x', 'y']]
    
        coords = [tuple(x) for x in subset.values]
    
    elif listVal == 'dict':
        geoDf["id"] = geoDf.index
        subset = geoDf[['id', 'x', 'y']]
        
        coords = subset.to_dict(orient='records')
    
    else:
        raise ValueError(
            'Value of listVal is not Valid. Please use "tuple" or "dict"'
        )
    
    return coords



def shp_to_qgslyr(shp, name=None):
    """
    OGR Compilant file to QGIS Vector Layer
    """

    from qgis.core import QgsVectorLayer

    from glass.pys.oss import fprop

    lyr = QgsVectorLayer(shp, name if name else fprop(shp, 'fn'), 'ogr')

    return lyr


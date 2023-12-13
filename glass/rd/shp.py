"""
Shape To some Python Object
"""

import os

def shp_to_obj(shp, geom_col=None, fields=None, output='df', srs_to=None,
    colsAsArray=None, geom_as_wkt=None, lyr=None, outgeom=None):
    """
    Feature Class to Python Object

    output Options:
    - df;
    - dict;
    - array;
    """

    import geopandas as gp

    if '.gdb' in shp and not lyr:
        lyr = os.path.basename(shp)
        shp = os.path.dirname(shp)

        if shp[-4:] != '.gdb':
            shp = os.path.dirname(shp)


    df = gp.read_file(shp) if not lyr else \
        gp.read_file(shp, layer=lyr)

    # Get name of geometry col
    if not geom_col:
        for c in df.columns.values:
            if c == 'geometry' or c == 'geom':
                geom_col = c
                break
    
    # Get Fields to Mantain
    if fields:
        from glass.pd.cols import del_cols_notin_ref

        df = del_cols_notin_ref(df, fields, geomCol=geom_col)
    
    # Project if necessary
    if srs_to and type(srs_to) == int:
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


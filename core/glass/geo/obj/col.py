"""
Objects Fields tools
"""


"""
Geom in Dataframes to columns
"""

def pointxy_to_cols(df, geomCol="geometry", colX="x", colY="y"):
    """
    Point x, y to cols

    TODO: check if geomtype if point or MultiPoint
    """
    
    df[colX] = df[geomCol].x.astype(float)
    df[colY] = df[geomCol].y.astype(float)
    
    return df


def geom_endpoints_to_cols(df, geomCol="geometry"):
    """
    Endpoints of Geometry in GeoDataframe to columns
    """
    
    def get_endpoints(row):
        coords = list(row[geomCol].coords)
        
        row["start_x"] = coords[0][0]
        row["start_y"] = coords[0][1]
        row["end_x"]   = coords[-1][0]
        row["end_y"]   = coords[-1][1]
        
        return row
    
    newDf = df.apply(lambda x: get_endpoints(x), axis=1)
    
    return newDf

"""
Download Views
"""

DOWNLOAD_DIR = ''

def kml_dsn_by_rqst(request, table, field, value):
    """
    Download data by filter
    """
    
    import os
    from glass.web.djg.ff.down import mdl_to_kml
    
    d_response = mdl_to_kml(
        table,
        "SELECT * FROM {} WHERE {}={}".format(table, field, value),
        os.path.join(DOWNLOAD_DIR, '{}_{}.kml'.format(table, str(value)))
    )
    
    return d_response


def kml_dsn_by_rqst_ij(request, table, tablepk,
                       jointbl, jointblpk,
                       rqstfk, rqst):
    """
    Download data by filter
    With Inner Join
    """
    
    import os
    from glass.web.djg.ff.down import mdl_to_kml
    
    SQL_QUERY = (
        "SELECT * FROM {tbl} INNER JOIN {jtbl} ON "
        "{tbl}.{tblpk} = {jtbl}.{jtblpk} "
        "WHERE {jtbl}.{rfk} = {rqstid}"
    ).format(
        tbl   = table  , jtbl   = jointbl,
        tblpk = tablepk, jtblpk = jointblpk,
        rfk   = rqstfk , rqstid = rqst
    )
    
    d_response = db_table_to_kml(
        table, SQL_QUERY,
        os.path.join(DOWNLOAD_DIR, '{}_{}.kml'.format(table, rqst))
    )
    
    return d_response


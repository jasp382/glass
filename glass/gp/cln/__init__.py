"""
Clean Geometries
"""

from glass.pys.oss import fprop
from glass.it.db   import shp_to_psql
from glass.sql.db  import create_pgdb
from glass.it.shp  import dbtbl_to_shp
from glass.prop.sql import db_exists


def remove_deadend(inShp, outShp, db=None):
    """
    Remove deadend
    """
    
    from glass.gp.cln.sql import rm_deadend
    
    # Create DB
    if not db:
        db = create_pgdb(fprop(inShp, 'fn', forceLower=True))
    
    else:
        isDb = db_exists(db)
        
        if not isDb:
            create_pgdb(db)
    
    # Send data to Database
    inTbl = shp_to_psql(db, inShp, api="shp2pgsql", encoding="LATIN1")
    
    # Produce result
    out_tbl = rm_deadend(db, inTbl, fprop(
        outShp, 'fn', forceLower=True))
    
    # Export result
    return dbtbl_to_shp(
        db, out_tbl, "geom", outShp, inDB='psql',
        tableIsQuery=None, api="pgsql2shp"
    )


def fix_geom_topo(shp, out, api='psql', db=None):
    """
    Fix geometries topology errors
    """

    if api == 'psql':
        from glass.gp.cln.sql import fix_geom

        # Create DB
        if not db:
            db = create_pgdb(fprop(shp, 'fn', forceLower=True))
    
        else:
            is_db = db_exists(db)

            if not is_db:
                create_pgdb(db)
    
        # Send Feature Class to the DB
        itbl = shp_to_psql(db, shp, api="ogr2ogr")

        # Produce result
        res = fix_geom(db, itbl, "geom")

        return dbtbl_to_shp(
            db, res, 'geom', out, api="ogr2ogr",
            tableIsQuery=True
        )
    
    elif api == 'pandas':
        from glass.rd.shp import shp_to_obj
        from glass.wt.shp import df_to_shp

        df = shp_to_obj(shp)

        df["geometry"] = df.geometry.make_valid()

        return df_to_shp(df, out)
    
    else:
        raise ValueError((
            'api value must be \'psql\', or \'pandas\''))



def rm_geom_errors(ishp, oshp, error=None):
    """
    Remove features with geometries not well formed (e.g. self
    intersection)
    """

    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    df = shp_to_obj(ishp)

    odf = df[df.geometry.is_valid]

    df_to_shp(odf, oshp)

    if error:
        edf = df[~df.geometry.is_valid]

        df_to_shp(edf, error)
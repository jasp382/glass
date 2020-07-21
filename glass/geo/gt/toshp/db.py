"""
Database Table to Shape
"""

def dbtbl_to_shp(db, tbl, geom_col, outShp, where=None, inDB='psql',
                 notTable=None, filterByReg=None, outShpIsGRASS=None,
                 tableIsQuery=None, api='psql', epsg=None):
    """
    Database Table to Feature Class file
    
    idDB Options:
    * psql
    * sqlite
    
    api Options:
    * psql
    * sqlite
    * pgsql2shp
    
    if outShpIsGRASS if true, the method assumes that outShp is
    a GRASS Vector. That implies that a GRASS Session was been
    started already. 
    """

    from glass.geo.gt.toshp import df_to_shp
    
    if outShpIsGRASS:
        from glass.pyt import execmd
        from glass.cons.psql import con_psql

        db_con = con_psql()
        
        whr = "" if not where else " where=\"{}\"".format(where)
        
        cmd_str = (
            "v.in.ogr input=\"PG:host={} dbname={} user={} password={} "
            "port={}\" output={} layer={} geometry={}{}{}{} -o --overwrite --quiet"
        ).format(
            db_con["HOST"], db, db_con["USER"], db_con["PASSWORD"],
            db_con["PORT"], outShp, tbl, geom_col, whr,
            " -t" if notTable else "", " -r" if filterByReg else ""
        ) if inDB == 'psql' else (
            "v.in.ogr -o input={} layer={} output={}{}{}{}"
        ).format(db, tbl, outShp, whr,
            " -t" if notTable else "", " -r" if filterByReg else ""
        ) if inDB == 'sqlite' else None
        
        rcmd = execmd(cmd_str)
    
    else:
        if api == 'pgsql2shp':
            from glass.pyt import execmd
            from glass.cons.psql import con_psql

            db_con = con_psql()
            
            outcmd = execmd((
                'pgsql2shp -f {out} -h {hst} -u {usr} -p {pt} -P {pas}{geom} '
                '{bd} {t}'
            ).format(
                hst=db_con['HOST'], usr=db_con["USER"], pt=db_con["PORT"],
                pas=db_con['PASSWORD'], bd=db, out=outShp,
                t=tbl if not tableIsQuery else '"{}"'.format(tbl),
                geom="" if not geom_col else " -g {}".format(geom_col)
            ))
        
        elif api == 'psql' or api == 'sqlite':
            from glass.dct.fm.sql import q_to_obj
            
            q = "SELECT * FROM {}".format(tbl) if not tableIsQuery else tbl
            
            df = q_to_obj(db, q, db_api=api, geomCol=geom_col, epsg=epsg)
            
            outsh = df_to_shp(df, outShp)
        
        else:
            raise ValueError((
                'api value must be \'psql\', \'sqlite\' or \'pgsql2shp\''))
    
    return outShp


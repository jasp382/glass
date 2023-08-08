"""
Geometry simplification
"""

def geom_simplification(db, tbl, selcols, geomc, simplifcationfactor, out):
    """
    Simplify table geometries
    """

    from glass.sql.q import exec_write_q
    from glass.pys   import obj_to_lst

    selcols = obj_to_lst(selcols)

    t = tbl if tbl.startswith("SELECT") else f"SELECT * FROM {tbl}"
    c = ", ".join(selcols)

    QS = [(
        f"CREATE TABLE {out} AS "
        f"SELECT {c}, ST_SimplifyPreserveTopology("
            f"{geomc}, {str(simplifcationfactor)}) AS {geomc} "
        f"FROM ({t}) AS foo"
    ), (
        f"CREATE INDEX {out}_{geomc}_dist "
        f"ON {out} USING gist({geomc})"
    )]

    exec_write_q(db, QS, api='psql')

    return out

"""
Geometry simplification
"""

def geom_simplification(db, tbl, selcols, geomc, simplifcationfactor, out):
    """
    Simplify table geometries
    """

    from glass.sql.q import exec_write_q
    from glass.pys import obj_to_lst

    selcols = obj_to_lst(selcols)

    QS = [(
        "CREATE TABLE {ot} AS "
        "SELECT {c}, ST_SimplifyPreserveTopology({g}, {sf}) AS {g} "
        "FROM ({t}) AS foo"
    ).format(
        ot=out, c=", ".join(selcols), g=geomc,
        t=tbl if tbl.startswith("SELECT") else "SELECT * FROM {}".format(tbl),
        sf=str(simplifcationfactor)
    ), (
        "CREATE INDEX {t}_{g}_dist ON {t} USING gist({g})"
    ).format(t=out, g=geomc)]

    exec_write_q(db, QS, api='psql')

    return out

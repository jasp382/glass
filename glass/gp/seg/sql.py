"""
Segmentation of Tables with geometries
"""

def geomseg_to_newtbl(db, tbl, pk, geom, geomtype, epsg, otbl,
                    cols=None, subdivide_factor=10):
    """
    Segmentation of geometry in table - 
    save results in a new table
    """

    from glass.sql.q import exec_write_q

    ctcols = "" if not cols else ", ".join([
        f"{c} {cols[c]}" for c in cols
    ]) + ", "

    selcols = "" if not cols else \
        ", ".join(list(cols.keys())) + ", "

    qs = [(
        f"CREATE TABLE {otbl} ("
            "sid uuid PRIMARY KEY, "
            f"{pk} integer REFERENCES {tbl}({pk}), "
            f"{ctcols}"
            f"geom geometry({geomtype}, {epsg})"
        ")"
    ), (
        f"CREATE INDEX {otbl}_geom_idx "
        f"ON {otbl} USING gist(geom)"
    ), (
        "CREATE EXTENSION IF NOT EXISTS "
        "\"uuid-ossp\""
    ), (
        f"INSERT INTO {otbl} "
        f"SELECT uuid_generate_v4(), {pk}, "
        f"{selcols}"
        f"ST_Subdivide({geom}, {subdivide_factor}) "
        f"FROM {tbl}"
    )]

    exec_write_q(db , qs, api='psql')

    return otbl


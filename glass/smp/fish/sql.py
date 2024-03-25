"""
Sampling SQL Tools
"""


def split_fishnetcells_in_four(db, table, cols, geom, epsg, last_id, outpk, pkorder, outshp=None, whr=None,
                               valascol=None):
    """
    Split fishnet pixels in four
    """

    from glass.sql.q import q_to_obj
    from glass.wt.shp import df_to_shp

    _cols = list(cols.keys())
    _whr = f' WHERE {whr}' if whr else ""

    val_as_col = "" if not valascol else ", ".join([f'{valascol[v]} AS {v}' for v in valascol]) + ', '

    fq = (
        f"SELECT {', '.join([f'{table}.{c}' for c in _cols])}, "
        f"ST_XMin({geom}) AS xleft, ST_XMax({geom}) AS xright, "
        f"ST_YMin({geom}) AS ybottom, ST_YMax({geom}) AS ytop, "
        f"(ST_XMax({geom}) - ST_XMin({geom})) / 2 AS xwidth, "
        f"(ST_YMax({geom}) - ST_YMin({geom})) / 2 AS yheight "
        f"FROM {table}{_whr}"
    )

    q = (
        f"SELECT {', '.join([f'foo.{c}' for c in _cols])}, "
        "ST_SetSRID(ST_Collect(ARRAY["
            "ST_MakePolygon(ST_MakeLine(ARRAY["
                "ST_MakePoint(xleft, ytop), "
            	"ST_MakePoint(xleft, ytop - yheight), "
            	"ST_MakePoint(xleft + xwidth, ytop - yheight), "
            	"ST_MakePoint(xleft + xwidth, ytop), "
            	"ST_MakePoint(xleft, ytop)"
            "])), "
            "ST_MakePolygon(ST_MakeLine(ARRAY["
            	"ST_MakePoint(xleft + xwidth, ytop),"
            	"ST_MakePoint(xleft + xwidth, ytop - yheight), "
            	"ST_MakePoint(xright, ytop - yheight), "
            	"ST_MakePoint(xright, ytop), "
            	"ST_MakePoint(xleft + xwidth, ytop)"
            "])),"
            "ST_MakePolygon(ST_MakeLine(ARRAY["
            	"ST_MakePoint(xleft, ytop - yheight), "
            	"ST_MakePoint(xleft, ybottom), "
            	"ST_MakePoint(xleft + xwidth, ybottom), "
            	"ST_MakePoint(xleft + xwidth, ytop - yheight), "
            	"ST_MakePoint(xleft, ytop - yheight)"
            "])), "
            "ST_MakePolygon(ST_MakeLine(ARRAY["
            	"ST_MakePoint(xleft + xwidth, ytop - yheight), "
            	"ST_MakePoint(xleft + xwidth, ybottom), "
            	"ST_MakePoint(xright, ybottom), "
            	"ST_MakePoint(xright, ytop - yheight), "
            	"ST_MakePoint(xleft + xwidth, ytop - yheight)"
            "]))"
        f"]), {str(epsg)}) AS {geom} "
        f"FROM ({fq}) AS foo"
    )

    fq = (
        f"SELECT ROW_NUMBER() OVER(ORDER BY {cols[pkorder]}) + {str(last_id)} AS {outpk}, "
        f"{val_as_col}* FROM ("
            f"SELECT {', '.join([f'foo2.{c} AS {cols[c]}' for c in cols])}, "
            f"(ST_Dump({geom})).geom AS {geom} "
            f"FROM ({q}) AS foo2"
        ") AS foo3"
    )

    subfish = q_to_obj(db, fq, geomCol=geom, epsg=epsg)

    if outshp:
        df_to_shp(subfish, outshp)

        return outshp
    
    return subfish


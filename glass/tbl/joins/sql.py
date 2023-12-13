


def join_by_intersect(db, tbl_a, tbl_b, id_a, geom_a, geom_b,
    otbl=None, cols_a=None, cols_b=None, whr_a=None, forcegeoma=None):
    """
    Join table A and table B.
    Join operation will be based on the intersection

    if one feature of table A intersects with more
    than one feature of Table B, the selected
    feature from table B will be the one occupying
    more area of feature A
    """

    from glass.sql.q import q_to_ntbl, q_to_obj
    from glass.prop.sql import cols_name

    if forcegeoma:
        ta_cols = cols_name(db, tbl_a)

        ta_cols.remove(geom_a)

        tacols_str = ", ".join([f"{tbl_a}.{c}" for c in ta_cols])

    if not cols_a and not cols_b:
        cols = 'foo.*'
        a_cols, b_cols = 'ta.*', 'tb.*'
    
    else:
        _cols = []

        if cols_a:
            _cols.extend(list(cols_a.keys()))

            a_cols = ", ".join([
                f"{cols_a[k]} AS {k}" for k in cols_a
            ])
        
        else:
            a_cols = ''
        
        if cols_b:
            _cols.extend(list(cols_b.keys()))

            b_cols = ", ".join([
                f"{cols_b[k]} AS {k}" for k in cols_b
            ])

            if a_cols:
                b_cols = ", " + b_cols
        
        else:
            b_cols = ''
    
        cols = ", ".join([f"foo.{c}" for c in _cols])

    whr_a = "" if not whr_a else f"{whr_a} AND "

    tbl_a = tbl_a if not forcegeoma else (
        f"(SELECT {tacols_str}, CASE "
        f"WHEN ST_IsValid({geom_a}) THEN {geom_a} "
        f"ELSE ST_MakeValid({geom_a}) END AS {geom_a} "
        f"FROM {tbl_a})"
    )

    calc_area = (
        f"ST_Area(ST_Intersection(ta.{geom_a}, tb.{geom_b})) / "
        f"ST_Area(ta.{geom_a}) * 100"
    )

    rn = (
        f"ROW_NUMBER() OVER (PARTITION BY {id_a} "
        f"ORDER BY {id_a}) AS idorder"
    )

    q = (
        f"SELECT {cols} FROM ("
            f"SELECT {a_cols}{b_cols}, "
            f"{calc_area} AS fa_area, "
            f"MAX({calc_area}) OVER(PARTITION BY "
                f"ta.{id_a} ORDER BY ta.{id_a}) AS maxarea "
            f"FROM {tbl_a} AS ta, {tbl_b} AS tb "
            f"WHERE {whr_a}"
            f"ST_Intersects(ta.geom, tb.geom) IS TRUE "
            f"ORDER BY ta.{id_a}"
        ") AS foo "
        "WHERE fa_area = maxarea "
    )

    # e possivel um poligono A intersectar-se 
    # com dois poligonos B. Estes dois poligonos
    # podem ocupar a mesma area do poligono A
    # Assim, o valor maximo e igual

    if otbl:
        _out = q_to_ntbl(db, otbl, q)
    
    else:
        if not cols_a or geom_a in cols_a:
            _out = q_to_obj(db, q, geomCol=geom_a)
        
        else:
            _out = q_to_obj(db, q)
    
    return _out


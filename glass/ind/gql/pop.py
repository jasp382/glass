"""
Produce indicators
"""


def points_by_pop(pnt_tbl, pop_tbl, id_pop, pop_col, outcol, countpnt='npnt'):
    """
    Useful to calculate pharmacies by 1000 inabitants
    """

    q = (
        "SELECT mtbl.*, "
        "CASE "
            f"WHEN jtbl.{countpnt} IS NULL "
            f"THEN 0 else jtbl.{countpnt} "
        f"END AS {countpnt} "
        "CASE "
            f"WHEN jtbl.{countpnt} IS NULL "
            f"THEN 0 ELSE (jtbl.{countpnt} /mtbl.{pop_col}) * 10000 "
        f"END AS {outcol} "
        f"FROM {pop_tbl} AS mtbl "
        "LEFT JOIN ("
            f"SELECT tpop.{id_pop}, COUNT({id_pop}) AS {countpnt} "
            f"FROM freg_pop AS tpop, {pnt_tbl} AS ptbl "
            "WHERE ST_Contains(tpop.geom, ptbl.geom) "
            f"GROUP BY tpop.{id_pop}"
        ") AS jtbl "
        f"ON mtbl.{id_pop} = jtbl.{id_pop}"
    )

    return q



def npoints_within_radius(main_tbl, main_pk, poly_tbl, poly_fk, pnt_tbl, radius, outcol):
    """
    Util para calcular numero de ecopontos
    a menos de 100 metros do centroide da bgri por 
    freguesia
    """

    q = (
        f"SELECT mb.*, jb.{outcol} "
        f"FROM {main_tbl} AS mb "
        "LEFT JOIN ("
	        f"SELECT b.{poly_fk}, COUNT(b.{poly_fk}) AS neco"
	        f"FROM {poly_tbl} AS b"
	        f"INNER JOIN {pnt_tbl} AS n"
	        f"ON ST_DWithin(ST_Centroid(b.geom), n.geom, {radius})"
	        f"GROUP BY b.{poly_fk}"
        f") AS jb ON mb.{main_pk} = jb.{poly_fk}"
    )

    return q


def areaperc_by_polygon(main_tbl, geom_tbl, whr_geom=None):
    """
    percentagem de floresta por freguesia
    """

    q = (
        "SELECT mt.*, "
        "(jfreg.iarea / ST_Area(mfreg.geom)) * 100 AS forestarea "
        f"FROM {main_tbl} AS mt "
        "LEFT JOIN ("
	        "SELECT mtbl.idfreg, "
	        "SUM(ST_Area(ST_Intersection(mtbl.geom, jtbl.geom))) AS iarea "
	        f"FROM {main_tbl} AS mtbl"
	        "LEFT JOIN ("
		        "SELECT cos2018_n1, n1, (ST_Dump(geom)).geom AS geom "
		        "FROM ("
			        "SELECT cos2018_n1, n1, "
			        "ST_UnaryUnion(ST_Collect(geom)) AS geom "
			        f"FROM {geom_tbl} "
			        #"WHERE n1='5' "
			        "GROUP BY cos2018_n1, n1"
		        ") AS foo"
	        ") AS jtbl "
	        "ON ST_Intersects(mtbl.geom, jtbl.geom) "
	        "GROUP BY mtbl.idfreg "
        ") AS jfreg ON mfreg.idfreg = jfreg.idfreg"
    )

    return q


def meantime_to_pnt():
    """
    tempo medio que se demora a chegar ao hospital mais proximo
    """

    q = (
        "SELECT mtbl.*, jtbl.timehosp FROM "
        "freg_cmb2 AS mtbl " 
        "LEFT JOIN ("
	        "SELECT bgri.idfreg, "
	        "SUM(((wthgen_nd * popres) / bgri_j.icol) * wthgen_nd) AS timehosp "
	        "FROM bgri "
	        "INNER JOIN ("
		        "SELECT idfreg, SUM(wthgen_nd * popres) AS icol "
		        "FROM bgri "
		        "GROUP BY idfreg"
	        ") AS bgri_j ON bgri.idfreg = bgri_j.idfreg "
	        "GROUP BY bgri.idfreg"
        ") AS jtbl "
        "ON mtbl.idfreg = jtbl.idfreg"
    )

    return q


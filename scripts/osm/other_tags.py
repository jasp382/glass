if __name__ == '__main__':
    db = 'osm_europe'
    Q = (
        "SELECT other_tags FROM multipolygons "
        "GROUP BY other_tags"
    )
    out_tbl = '/home/osmtolulc/mrgis/other_tags.xlsx'

    from glass.to import db_to_tbl

    db_to_tbl(db, Q, out_tbl)


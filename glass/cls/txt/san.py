"""
Sanitize data for Text Classification
"""

def get_stop_words(inTbl, fidCol, txtCol, outFile,
                   lang='portuguese', inSheet=None, db=None):
    """
    Pick a text column and save it in a new column only with the stop words.
    
    Uses PostgreSQL dictionaries to get stop words
    """
    
    from glass.pys.oss  import fprop
    from glass.prop.sql import cols_name
    from glass.sql.db   import create_pgdb
    from glass.it.db    import tbl_to_db
    from glass.it       import db_to_tbl
    
    FILENAME = fprop(inTbl, 'fn')
    
    # Create Temp database
    db = create_pgdb(f"db_{FILENAME}" if not db else db)
    
    # Send table to PostgreSQL
    tbl = tbl_to_db(inTbl, db, FILENAME, sheet=inSheet, api_db='psql')
    
    cols = cols_name(db, tbl, sanitizeSpecialWords=None, api='psql')
    
    # Sanitize data  and create a new column only with stop words
    Q1 = (
        "(SELECT *, to_tsvector('{_lang}', regexp_replace("
            "regexp_replace(lower(unaccent({txt_c})), 'http://[^:\s]+(\S+)', "
            "' ', 'g'), '[^\w]+', ' ', 'g')) "
        "AS txt_data FROM {t}) AS stop_table"
    ).format(_lang=lang, txt_c=txtCol, t=tbl)
    
    Q2 = (
        "SELECT {selCols}, ARRAY_TO_STRING(array_agg("
            "word ORDER BY word_index), ' ', '*') AS {outCol}, "
        "REPLACE(CAST(STRIP("
            "stop_table.txt_data) AS text), '''', '') AS no_duplicated "
        "FROM ("
            "SELECT fid, word, CAST(UNNEST(word_index) AS integer) "
            "AS word_index FROM ("
                "SELECT fid, SPLIT_PART(tst, ';', 1) AS word, "
                "STRING_TO_ARRAY(SPLIT_PART(tst, ';', 2), ',') AS word_index FROM ("
                    "SELECT {fid} AS fid, REPLACE(REPLACE(REPLACE(REPLACE(REPLACE("
                        "CAST(UNNEST(txt_data) AS text), "
                            "',{{', ',\"{{'), ',\"{{', ';'), '}}\"', ''), "
                            "'(', ''), '}}', '') AS tst "
                    "FROM {tbl}"
                ") AS foo"
            ") AS foo2"
        ") AS foo3 INNER JOIN {tbl} ON foo3.fid = stop_table.{fid} "
        "GROUP BY {selCols}, stop_table.txt_data"
    ).format(
        outCol="clean_" + txtCol, tbl=Q1, fid=fidCol,
        selCols=", ".join(["stop_table.{}".format(i) for i in cols])
    )
    
    # Export new table
    return db_to_tbl(db, Q2, outFile, sheetsNames=inSheet)


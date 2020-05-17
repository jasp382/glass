"""
Split table methods
"""

def split_table_by_range(db, table, row_number):
    """
    Split tables in several
    """
    
    from glass.ng.prop.sql import cols_name, row_num
    from glass.ng.sql.q import q_to_ntbl
    
    rowsN = row_num(db, table, api='psql')
    
    nrTables = int(rowsN / float(row_number)) + 1
    
    COLS = cols_name(db, table)
    
    offset = 0
    for i in range(nrTables):
        q_to_ntbl(
            db, '{}_{}'.format(table, str(i)),
            "SELECT * FROM {} ORDER BY {} OFFSET {} LIMIT {} ;".format(
                table, ', '.join(COLS), str(offset), str(row_number) 
            ), api='psql'
        )
        
        offset += row_number


def split_table_entity_number(db, table, entity_field, entity_number):
    """
    Split tables in several using as reference a number of entities per table
    
    If a table has 1 000 000 entities and the entity_number is 250 000,
    this method will create four tables, each one with 250 000 entities.
    250 000 entities, not rows. Don't forget that the main table may have
    more than one reference to the same entity.
    """
    
    from glass.ng.sql.q    import q_to_obj
    from glass.ng.prop.sql import cols_type
    from glass.ng.sql.q    import q_to_ntbl
    
    # Select entities in table
    entities = q_to_obj(db, "SELECT {c} FROM {t} GROUP BY {c}".format(
        c=entity_field, t=table
    ), db_api='psql')
    
    # Split entities into groups acoording entity_number
    entityGroup = []
    
    lower = 0
    high = entity_number
    while lower <= len(entities.index):
        if high > len(entities.index):
            high = len(entities.index)
        
        entityGroup.append(entities.iloc[lower : high])
        
        lower += entity_number
        high  += entity_number
    
    # For each dataframe, create a new table
    COLS_TYPE = cols_type(db, table)
    
    c = 0
    for df in entityGroup:
        if COLS_TYPE[entity_field] != str:
            df[entity_field] = '{}='.format(entity_field) + df[entity_field].astype(str)
        else:
            df[entity_field] = '{}=\''.format(entity_field) + df[entity_field].astype(str) + '\''
        
        whr = ' OR '.join(df[entity_field])
        
        q_to_ntbl(db, '{}_{}'.format(table, str(c)), (
            "SELECT * FROM {} WHERE {}"
        ).format(table, whr), api='psql')
        
        c += 1


def split_table_by_col_distinct(db, tbl, col):
    """
    Create a new table for each value in one column
    """
    
    from glass.ng.sql.q    import q_to_obj
    from glass.ng.prop.sql import cols_type
    from glass.ng.sql.q    import q_to_ntbl
    
    fields_types = cols_type(db, tbl)
    
    # Get unique values
    VALUES = q_to_obj(db,
        "SELECT {col} FROM {t} GROUP BY {col}".format(
            col=col, t=tbl
        ), db_api='psql'
    )[col].tolist()
    
    whr = '{}=\'{}\'' if fields_types[col] == str else '{}={}'
    
    for row in VALUES:
        q_to_ntbl(
            db, '{}_{}'.format(tbl, str(row[0])),
            "SELECT * FROM {} WHERE {}".format(
                tbl, whr.format(col, str(row[0]))
        ), api='psql')


"""
Execute queries to extract data from a PGSQL Database
"""

import os;            import pandas
from glass.dct.fm.sql import q_to_obj
from glass.dct.to     import obj_to_tbl


def count_by_periods_with_certain_duration(db, PERIOD_INTERVAL, pgtable,
                                           TIME_FIELD, outTable,
                                           filterWhere=None):
    """
    Count rows in a pgtable by periods of X minutes
    
    PERIOD_INTERVAL = "01:00:00"
    """
    
    import pandas
    from glass.pyt.tm import day_to_intervals2
    
    # Get Intervals
    INTERVALS = day_to_intervals2(PERIOD_INTERVAL)
    
    # For each interval/period, count the number of rows
    counting = None
    for _int_ in INTERVALS:
        QUERY = (
            "SELECT COUNT(*) AS count FROM {table} WHERE "
            "TO_TIMESTAMP({timeCol}, 'HH24:MI:SS') >= "
            "TO_TIMESTAMP('{minLower}', 'HH24:MI:SS') AND "
            "TO_TIMESTAMP({timeCol}, 'HH24:MI:SS') < "
            "TO_TIMESTAMP('{minUpper}', 'HH24:MI:SS'){whr}"
        ).format(
            table    =  pgtable, timeCol  = TIME_FIELD,
            minLower = _int_[0], minUpper =   _int_[1],
            whr      = "" if not filterWhere else " AND ({})".format(
                filterWhere
            )
        )
        
        count = q_to_obj(db, QUERY, db_api='psql')
        
        count.rename(index={0 : "{}-{}".format(
            _int_[0][:5], _int_[1][:5]
        )}, inplace=True)
        
        if type(counting) != pandas.DataFrame:
            counting = count.copy()
        
        else:
            counting = counting.append(count, ignore_index=False)
    
    obj_to_tbl(counting, outTable)
    
    return outTable


def count_entity_periods_with_certain_duration(db, PERIOD_INTERVAL,
                                               PGTABLE, TIME_FIELD, ENTITY_FIELD,
                                               OUT_TABLE, filterWhere=None):
    """
    Count rows in a pgtable for a given period of X minutes for each
    interest entity
    
    PERIOD_INTERVAL = "01:00:00"
    """
    
    import pandas
    from glass.pyt.tm       import day_to_intervals2
    from glass.pyt.df.joins import combine_dfs
    
    # Get Intervals
    INTERVALS = day_to_intervals2(PERIOD_INTERVAL)
    
    # For each interval/period, count the number of rows by entity
    counting = []
    for _int in INTERVALS:
        Q = (
            "SELECT {entityCol}, COUNT({entityCol}) AS {cntCol} "
            "FROM {table} WHERE "
            "TO_TIMESTAMP({timeCol}, 'HH24:MI:SS') >= "
            "TO_TIMESTAMP('{minLower}', 'HH24:MI:SS') AND "
            "TO_TIMESTAMP({timeCol}, 'HH24:MI:SS') < "
            "TO_TIMESTAMP('{minUpper}', 'HH24:MI:SS'){whr} "
            "GROUP BY {entityCol}"
        ).format(
            cntCol = "s{}_e{}".format(_int[0][:5], _int[1][:5]).replace(":", "_"),
            table  = PGTABLE, timeCol=TIME_FIELD, entityCol=ENTITY_FIELD,
            minLower=_int[0], minUpper=_int[1],
            whr = "" if not filterWhere else " AND ({}) ".format(filterWhere)
        )
        
        count = q_to_obj(db, Q, db_api='psql')
        
        counting.append(count)
    
    mainDf = combine_dfs(counting[0], counting[1:], ENTITY_FIELD)
    
    obj_to_tbl(mainDf, OUT_TABLE)
    
    return OUT_TABLE


def count_by_groupcols_and_periods(db, pgtable, COLUMNS_TO_GROUP,
                                   HOUR_FIELD, MINUTES_FIELD, COUNT_FIELD_NAME,
                                   OUTPUT_FILE,
                                   PERIOD_INTERVAL=None, PERIODS=None):
    """
    Count rows in a pgtable by periods of X minutes grouping by columns values
    """
    
    from glass.pyt.tm import day_to_intervals
    
    if not PERIODS and not PERIOD_INTERVAL:
        raise ValueError((
            "Please give value to PERIODS or PERIODS_INTERAL. "
            "If PERIODS and PERIODS_INTERVAL, PERIODS will have priority."
        ))
    
    INTERVALS = day_to_intervals(PERIOD_INTERVAL) if not PERIODS else PERIODS
    
    i = 0
    for interval in INTERVALS:
        start, end = interval
        
        INTERVAL_STR = '{}h{}-{}h{}'.format(start[0], start[1], end[0], end[1])
        
        if start[0] == end[0]:
            QUERY = (
                "SELECT {cols}, COUNT({col}) AS {countname} FROM {table} "
                "WHERE {hourF}={hour} AND "
                "{minF} >= {minLower} AND {minF} < {minUpper} "
                "GROUP BY {cols}"
            ).format(
                table=pgtable, cols=', '.join(COLUMNS_TO_GROUP),
                col=COLUMNS_TO_GROUP[0], countname=COUNT_FIELD_NAME,
                hourF=HOUR_FIELD, hour=str(start[0]),
                minF=MINUTES_FIELD, minLower=str(start[1]), minUpper=str(end[1])
            )
        
        else:
            if end[0] - start[0] == 1:
                QUERY = (
                    "SELECT {cols}, COUNT({col}) AS {countname} FROM {table} "
                    "WHERE ({hourF}={hourLower} AND {minF}>={minLower}) OR "
                    "({hourF}={hourUpper} AND {minF} < {minUpper}) "
                    "GROUP BY {cols}"
                ).format(
                    table=pgtable, cols=', '.join(COLUMNS_TO_GROUP),
                    col=COLUMNS_TO_GROUP[0], countname=COUNT_FIELD_NAME,
                    hourF=HOUR_FIELD, hourLower=str(start[0]), hourUpper=str(end[0]),
                    minF=MINUTES_FIELD, minLower=str(start[1]), minUpper=str(end[1])
                )
            
            else:
                mHours = [start[0] + i for i in range(1, end[0] - start[0])]
                
                QUERY = (
                    "SELECT {cols}, COUNT({col}) AS {countname} FROM {table} "
                    "WHERE ({hourF}={hourLower} AND {minF}>={minLower}) OR "
                    "{mean_hours_exp} OR "
                    "({hourF}={hourUpper} AND {minF} < {minUpper}) "
                    "GROUP BY {cols}"
                ).format(
                    table=pgtable, cols=', '.join(COLUMNS_TO_GROUP),
                    col=COLUMNS_TO_GROUP[0], countname=COUNT_FIELD_NAME,
                    hourF=HOUR_FIELD, hourLower=str(start[0]), hourUpper=str(end[0]),
                    minF=MINUTES_FIELD, minLower=str(end[1]), minUpper=str(end[1]),
                    mean_hours_exp=" OR ".join([
                        "({}={} AND {} >= 0)".format(
                            HOUR_FIELD, h, MINUTES_FIELD
                        ) for h in mHours
                    ])
                )
        
        countTbl = q_to_obj(db, QUERY, db_api='psql')
        
        countTbl[HOUR_FIELD] = INTERVAL_STR
        
        if not i:
            table = countTbl
            i+=1
        else:
            table = table.append(countTbl, ignore_index=True)
    
    obj_to_tbl(table, OUTPUT_FILE)


def sel_where_groupByIs(db, table, groupByCols, grpByOp, grpByVal, outTable,
                        filterWhere=None):
    """
    Select rows in table where the GROUP BY values of the groupByCols agrees with
    the statment formed by grpByOp and grpByVal
    
    For the following parameters:
    table=tst_table, groupByCols=[day, hour], grpByOp=>, grpByVal=1
    
    This method will create a new table using a query such
    SELECT tst_table.* FROM tst_table INNER JOIN (
        SELECT day, hour, COUNT(day) AS cnt_day FROM tst_table
        GROUP BY day, hour
    ) AS foo ON tst_table.day = foo.day AND tst_table.hour = foo.hour
    WHERE foo.cnt_day > 1
    """
    
    from glass.pyt        import obj_to_lst
    from glass.dct.to.sql import q_to_ntbl
    
    groupByCols = obj_to_lst(groupByCols)
    
    q = (
        "SELECT {t}.* FROM {t} INNER JOIN ("
            "SELECT {cls}, COUNT({col}) AS cnt_{col} "
            "FROM {t} GROUP BY {cls}"
        ") AS foo ON {jOn} "
        "WHERE foo.cnt_{col} {op} {val}{fwhr}"
    ).format(
        t=table, cls=", ".join(groupByCols),
        col=groupByCols[0],
        jOn=" AND ".join(["{t}.{c} = foo.{c}".format(
            t=table, c=x) for x in groupByCols]),
        op=grpByOp, val=grpByVal,
        fwhr="" if not filterWhere else " AND ({})".format(filterWhere)
    )
    
    outTable = q_to_ntbl(db, outTable, q, api='psql')
    
    return outTable

def count_rows_by_entity_and_shpJoin(dbn, PG_TABLE, PG_ENTITY, PG_PIVOT_COL,
                                     SHP_TABLE, SHP_ENTITY, RESULT_SHP,
                                     WHERE=None):
    """
    Select and GROUP BY attrs generating a table as:

    ENTITY | ATTR_N | COUNT
       1   | 12ECIR |   X
       2   | 12ECIR |   X
       1   | 15ECIR |   X
       2   | 15ECIR |   X

    Then convert this table to the following
    ENTITY | 12ECIR | 15ECIR
       1   |   X    |   X
       2   |   X    |   X
    
    The last table will be joined with a given Shapefile
    
    TODO: See if PGSQL crosstab works to solve this problem
    """
    
    from glass.dct.fm       import tbl_to_obj
    from glass.dct.fm.sql   import q_to_obj
    from glass.pyt.df       import series_to_list
    from glass.geo.gt.toshp import df_to_shp
    from glass.pyt.df.joins import combine_dfs
    from glass.dct.to.sql   import q_to_ntbl
    from glass.sql.tbl      import del_tables
    
    
    # Get GROUP BYed data
    # Get row counting using GROUPBY with ENTITY AND PIVOT_COL
    q = ("SELECT {entity}, {pivc}, COUNT({entity}) AS n{entity} "
         "FROM {tbl} {whr}GROUP BY {entity}, {pivc}").format(
        entity=PG_ENTITY, tbl=PG_TABLE, pivc=PG_PIVOT_COL,
        whr="" if not WHERE else "WHERE {} ".format(WHERE)
    )
    
    selData = q_to_ntbl(dbn, "seldata", q, api='psql')
    
    # Get columns of the output table
    pivotCols = q_to_obj(dbn,
        "SELECT {piv} FROM {tb} GROUP BY {piv}".format(
            tb=selData, piv=PG_PIVOT_COL
        ), db_api='psql'
    )
    pivotCols = series_to_list(pivotCols[PG_PIVOT_COL])
    
    # Get data for each new column - new column data in one dataframe
    pre_pivot = [q_to_obj(dbn,
        "SELECT {entity}, n{entity} FROM {t} WHERE {c}='{pivcol}'".format(
            entity=PG_ENTITY, t=selData, c=PG_PIVOT_COL, pivcol=col
        ), db_api='psql'
    ) for col in pivotCols]
    
    # In pre_pivot DF, give the correct name to the n{entity} column
    for i in range(len(pre_pivot)):
        pre_pivot[i].rename(columns={
            "n{}".format(PG_ENTITY) : pivotCols[i]
        }, inplace=True)
    
    # Join all dataframes into one
    pivot_df = pre_pivot[0]
    pivot_df = combine_dfs(pivot_df, pre_pivot[1:], PG_ENTITY)
    
    # Join pivot_df to the Given ESRI Shapefile
    shpDf = tbl_to_obj(SHP_TABLE)
    
    shpDf = shpDf.merge(pivot_df, how='outer',
                        left_on=SHP_ENTITY, right_on=PG_ENTITY)
    
    df_to_shp(shpDf, RESULT_SHP)
    
    del_tables(dbn, selData)
    
    return RESULT_SHP


"""
Get Means
"""


def meandays_by_entity(db, pgtable, DAY_FIELD, ENTITY_FIELD,
                       COUNT_FIELD_NAME, OUTPUT_FILE, EXCLUDE_DAYS=None):
    """
    For every day in a pgtable, count the number of rows for each interest entity.
    At the end, calculate the mean of rows between every day for each entity.
    
    Day field must be of type text
    """
    
    from glass.sql.q import q_to_obj
    from glass.wt    import obj_to_tbl
    
    # Get days
    VALUES = q_to_obj(db, 
        "SELECT {col} FROM {t} GROUP BY {col}".format(
            col=DAY_FIELD, t=pgtable
        ), db_api='psql'
    )[DAY_FIELD].tolist()
    
    # For every day, Group rows by entities
    tableArray = []
    for day in VALUES:
        if EXCLUDE_DAYS:
            if day[0] in EXCLUDE_DAYS:
                continue
        
        QUERY = (
            "SELECT {col}, COUNT({col}) AS {countname} FROM {table} "
            "WHERE {dayF}='{d}' GROUP BY {col}"
        ).format(
            col=ENTITY_FIELD, countname=COUNT_FIELD_NAME,
            table=pgtable, dayF=DAY_FIELD, d=day[0]
        )
        
        countTbl = q_to_obj(db, QUERY, db_api='psql')
        
        tableArray.append(countTbl)
    
    # Get mean for all entities
    main_table = tableArray[0]
    TMP_COUNT_FIELD_NAME = 'join_' + COUNT_FIELD_NAME
    TMP_JOIN_FIELD = 'id_entity'
    
    for i in range(1, len(tableArray)):
        tableArray[i].rename(columns={
            COUNT_FIELD_NAME: TMP_COUNT_FIELD_NAME,
            ENTITY_FIELD: TMP_JOIN_FIELD}, inplace=True)
        
        main_table = main_table.merge(
            tableArray[i], how='outer', left_on=ENTITY_FIELD,
            right_on=TMP_JOIN_FIELD
        )
        
        main_table.fillna(0, inplace=True)
        main_table[ENTITY_FIELD].replace(
            0, main_table[TMP_JOIN_FIELD], inplace=True)
        
        main_table[COUNT_FIELD_NAME] = main_table[COUNT_FIELD_NAME] + \
            main_table[TMP_COUNT_FIELD_NAME]
        main_table.drop([
            TMP_COUNT_FIELD_NAME, TMP_JOIN_FIELD], axis=1, inplace=True)
    
    main_table[COUNT_FIELD_NAME] = main_table[COUNT_FIELD_NAME] / len(tableArray)
    
    obj_to_tbl(main_table, OUTPUT_FILE)

    return OUTPUT_FILE


def meanrowsday_by_entity(psqldb, pgtable, dayField, entityField, out_file,
                          filterData=None, newMeanField=None, numberDays=None):
    """
    For every day in a pgtable, count the number of rows for each interest entity.
    At the end, calculate the mean of rows between every day for each entity.
    
    Day field must be of type text
    
    Difference in relation to meandays_by_entity:
    this one uses only SQL and PGSQL and not Pandas.
    
    if numberDays=None, the number of days used will be based on the days
    included in the data. If you want the mean for 5 days, but there are no data
    for one of these days, with numberDays=None, the mean will be only for
    4 days.
    """
    
    from glass.pys      import obj_to_lst
    from glass.sql.q import q_to_obj
    from glass.wt    import obj_to_tbl
    
    entityField = obj_to_lst(entityField)
    mean_field  = "mean_rows" if not newMeanField else newMeanField
    
    ndaysQ = "SELECT {} AS nday".format(numberDays) if numberDays else \
        ("SELECT MAX(nday) AS nday FROM ("
            "SELECT row_number() OVER(ORDER BY {dayF}) AS nday "
            "FROM {t} {whr}"
            "GROUP BY {dayF}"
        ") AS fooday").format(
            whr="" if not filterData else "WHERE {} ".format(filterData),
            dayF=dayField, t=pgtable
        )
    
    # Get mean rows of all days by entity
    q = (
        "SELECT {entityF}, (SUM(conta) / nday) AS {mF} "
        "FROM ("
            "SELECT {entityF}, {dayF}, COUNT({cnt}) AS conta "
            "FROM {t} {whr}"
            "GROUP BY {entityF}, {dayF}"
        ") AS foo, ({getD}) AS foo2 "
        "GROUP BY {entityF}, nday"
    ).format(
        entityF=", ".join(entityField),
        dayF=dayField, mF=mean_field,
        cnt=entityField[0], t=pgtable,
        whr="" if not filterData else "WHERE {} ".format(filterData),
        getD=ndaysQ
    )
    
    data = q_to_obj(psqldb, q, db_api='psql')
    
    obj_to_tbl(data, out_file)
    
    return out_file


def meanday_of_periods_by_entity(psqldb, pgtable, DAY_FIELD, HOUR_FIELD,
                                 MINUTES_FIELD, ENTITY_FIELD, OUTPUT_FILE,
                                 PERIODS=None, PERIODS_INTERVAL=None,
                                 EXCLUDE_DAYS=None, workspace_day_tables=None):
    """
    For every day in a pgtable, count the number of rows by periods of X minutes
    for each interest entity.
    
    At the end, calculate the mean between every day for each period.
    """
    
    import os
    from glass.pys.tm         import day_to_intervals
    from glass.pd.joins    import combine_dfs
    from glass.sql.q       import q_to_obj
    from glass.wt          import obj_to_tbl
    from glass.sql.q.count import count_by_period_entity
    
    if not PERIODS and not PERIODS_INTERVAL:
        raise ValueError((
            "Please give value to PERIODS or PERIODS_INTERAL. "
            "If PERIODS and PERIODS_INTERVAL, PERIODS will have priority."
        ))
    
    # Get intervals
    INTERVALS = day_to_intervals(PERIODS_INTERVAL) if not PERIODS else PERIODS
    
    # Get unique values
    VALUES = q_to_obj(psqldb, "SELECT {col} FROM {t} GROUP BY {col}".format(
        col=DAY_FIELD, t=pgtable
    ))[DAY_FIELD].tolist()
    
    DAYS_ARRAY       = []
    INTERVAL_COLUMNS = []
    
    def get_day_table(day):
        print('Starting: ' + day)
        
        if EXCLUDE_DAYS:
            if day in EXCLUDE_DAYS:
                print('Ending: ' + day)
                return 0
        
        COUNTING = []
        for __int in INTERVALS:
            start, end = __int
            COUNT_FIELD = 'p{}h{}_{}h{}'.format(
                str(start[0]), str(start[1]), str(end[0]), str(end[1])
            )
            
            if COUNT_FIELD not in INTERVAL_COLUMNS:
                INTERVAL_COLUMNS.append(COUNT_FIELD)
            
            countTbl = count_by_period_entity(
                psqldb, start, end,
                pgtable, DAY_FIELD, day,
                HOUR_FIELD, MINUTES_FIELD, ENTITY_FIELD
            )
            COUNTING.append(countTbl)
        
        main_table = COUNTING[0]
        for i in range(1, len(COUNTING)):
            main_table = combine_dfs(main_table, COUNTING[i], ENTITY_FIELD)
        
        if workspace_day_tables:
            obj_to_tbl(
                main_table, os.path.join(workspace_day_tables, 'ti_{}.xlsx')
            )
        
        return main_table
    
    for day in VALUES:
        t = get_day_table(day[0])
        if type(t) == int:
            continue
        else:
            DAYS_ARRAY.append(t)
        
        print('Ending: ' + day[0])
    
    main_table = DAYS_ARRAY[0]
    
    for i in range(1, len(DAYS_ARRAY)):
        join_field = 'id_entity'
        
        renameDict = {col: 'join_' + col for col in INTERVAL_COLUMNS}
        renameDict.update({ENTITY_FIELD : join_field})
        
        DAYS_ARRAY[i].rename(columns=renameDict, inplace=True)
        
        main_table = main_table.merge(
            DAYS_ARRAY[i], how='outer',
            left_on=ENTITY_FIELD, right_on=join_field
        )
        
        main_table.fillna(0, inplace=True)
        main_table[ENTITY_FIELD].replace(
            0, main_table[join_field], inplace=True
        )
        
        main_table.drop(join_field, axis=1, inplace=True)
        for k in INTERVAL_COLUMNS:
            main_table[k] = main_table[k] + main_table[renameDict[k]]
            main_table.drop(renameDict[k], axis=1, inplace=True)
    
    for col in INTERVAL_COLUMNS:
        main_table[col] = main_table[col] / len(DAYS_ARRAY)
    
    obj_to_tbl(main_table, OUTPUT_FILE)


def meanrowsday_of_periods_by_entity(psql_con, pgtable, dayField, hourField,
                                     minutesField, secondField, entityField,
                                     PERIODS, outFile,
                                     filterData=None, numberDays=None):
    """
    Evolution of meanday_of_periods_by_entity:
    For every day in a pgtable, count the number of rows by periods of X minutes
    for each interest entity.
    
    At the end, calculate the mean between every day for each period.
    
    This method uses SQL and TimeInterval columns.
    
    PERIODS = [('07:30:00', '09:30:00'), ('07:30:00', '09:30:00')]
    
    It is not complete because the output table not have a column for each
    period
    """
    
    from glass.pys      import obj_to_lst
    from glass.sql.q import q_to_obj
    from glass.wt    import obj_to_tbl
    
    def get_case(PTUPLE, PFIELD):
        return (
            "CASE "
                "WHEN TO_TIMESTAMP("
                    "COALESCE(CAST({h} AS text), '') || ':' || "
                    "COALESCE(CAST({m} AS text), '') || ':' || "
                    "COALESCE(CAST({s} AS text), ''), 'HH24:MI:SS'"
                ") >= TO_TIMESTAMP('{tLower}', 'HH24:MI:SS') AND "
                "TO_TIMESTAMP("
                    "COALESCE(CAST({h} AS text), '') || ':' || "
                    "COALESCE(CAST({m} AS text), '') || ':' || "
                    "COALESCE(CAST({s} AS text), ''), 'HH24:MI:SS'"
                ") < TO_TIMESTAMP('{tUpper}', 'HH24:MI:SS') "
                "THEN 1 ELSE 0 "
            "END AS {fld}"
        ).format(
            h=hourField, m=minutesField, s=secondField,
            tLower=PTUPLE[0], tUpper=PTUPLE[1],
            fld=PFIELD
        )
    
    entityField = obj_to_lst(entityField)
    
    periodsCols = [
        "p{ha}h{ma}_{hb}h{mb}".format(
            ha=p[0].split(':')[0], ma=p[0].split(':')[1],
            hb=p[1].split(':')[0], mb=p[1].split(':')[1]
        ) for p in PERIODS
    ]
    
    ndaysQ = "SELECT {} AS nday".format(numberDays) if numberDays else \
        ("SELECT MAX(nday) AS nday FROM ("
            "SELECT row_number() OVER(ORDER BY {dayF}) AS nday "
            "FROM {t} {whr}"
            "GROUP BY {dayF}"
        ") AS dayt")
    
    # Get mean rows of all days by entity and period
    q = (
        "SELECT {entityF}, {meanSq}, nday FROM ("
            "SELECT {entityF}, {dayF}, {sumSeq} FROM ("
                "SELECT {entityF}, {dayF}, {caseSt} FROM {t} {whr}"
            ") AS foo "
            "WHERE {whrSq} "
            "GROUP BY {entityF}, {dayF}"
        ") AS foo2, ({getND}) AS fooday "
        "GROUP BY {entityF}, nday"
    ).format(
        entityF = ", ".join(entityField),
        meanSq  = ", ".join([
            "(SUM({f}) / nday) AS {f}".format(f=p) for p in periodsCols
        ]),
        dayF    = dayField,
        sumSeq  = ", ".join([
            "SUM({f}) AS {f}".format(f=p) for p in periodsCols
        ]),
        caseSt=", ".join([
            get_case(PERIODS[x], periodsCols[x]) for x in range(len(PERIODS))
        ]),
        t=pgtable,
        whr="" if not filterData else "WHERE {} ".format(filterData),
        whrSq=" OR ".join(["{}=1".format(p) for p in periodsCols]),
        getND=ndaysQ
    )
    
    data = q_to_obj(psql_con, q, db_api='psql')
    
    obj_to_tbl(data, outFile)
    
    return outFile


def matrix_od_mean_dist_by_group(MATRIX_OD, ORIGIN_COL, GROUP_ORIGIN_ID,
                                 GROUP_ORIGIN_NAME, GROUP_DESTINA_ID,
                                 GROUP_DESTINA_NAME, TIME_COL, epsg, db,
                                 RESULT_MATRIX):
    """
    Calculate Mean GROUP distance from OD Matrix
    
    OD MATRIX EXAMPLE
    | origin_entity | origin_group | destina_entity | destina_group | distance
    |     XXXX      |     XXXX     |      XXXX      |      XXX      |   XXX
    
    OUTPUT EXAMPLE
    | origin_group | destina_group | mean_distance
    |     XXXX     |      XXXX     |      XXXX
    """
    
    from glass.pys.oss   import fprop
    from glass.it.db  import shp_to_psql
    from glass.sql.db import create_pgdb
    from glass.sql.q  import q_to_ntbl
    from glass.it     import db_to_tbl
    
    db = create_pgdb(fprop(MATRIX_OD, 'fn'), overwrite=True)
    
    TABLE = shp_to_psql(
        db, MATRIX_OD, pgTable=f"tbl_{db}",
        api="pandas", srs=epsg
    )
    
    OUT_TABLE = q_to_ntbl(db, fprop(RESULT_MATRIX, 'fn'), (
        f"SELECT {GROUP_ORIGIN_ID}, {GROUP_ORIGIN_NAME}, {GROUP_DESTINA_ID}, "
        f"{GROUP_DESTINA_NAME}, AVG(mean_time) AS mean_time FROM ("
            f"SELECT {ORIGIN_COL}, {GROUP_ORIGIN_ID}, {GROUP_ORIGIN_NAME}, "
            f"{GROUP_DESTINA_ID}, {GROUP_DESTINA_NAME}, "
            f"AVG({TIME_COL}) AS mean_time FROM {TABLE} "
            f"GROUP BY {ORIGIN_COL}, {GROUP_ORIGIN_ID}, {GROUP_ORIGIN_NAME}, "
            f"{GROUP_DESTINA_ID}, {GROUP_DESTINA_NAME}"
        ") AS foo "
        f"GROUP BY {GROUP_ORIGIN_ID}, {GROUP_ORIGIN_NAME}, "
        f"{GROUP_DESTINA_ID}, {GROUP_DESTINA_NAME} "
        f"ORDER BY {GROUP_ORIGIN_ID}, {GROUP_DESTINA_ID}"
    ), api='psql')
    
    return db_to_tbl(
        db, f"SELECT * FROM {OUT_TABLE}", RESULT_MATRIX,
        sheetsNames="matrix", dbAPI='psql'
    )


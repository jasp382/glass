"""
Filter PostgreSQL Table Data and create charts in XLS File
with that data
"""


def bar_chart_by_query(db, query, xaxis_col, chart_data_fld_name,
                       series, outxls):
    """
    Execute some query for each serie in series.
    Produce a bar chart with the data returned.
    Each serie will be new bar in the chart.
    So, the query statment must have a white space
    to put each serie in series... E.g.:
    "SELECT fld_name FROM t WHERE series_fld={}".format(serie in series)
    """
    
    from glass.dct.fm.sql     import q_to_obj
    from glass.pyt.df.joins   import combine_dfs
    from glass.pyt.xls.charts import barchart_in_xls_from_df
    
    dataDf = []
    for serie in series:
        data = q_to_obj(db, query.format(serie), db_api='psql')
        data.rename(columns={chart_data_fld_name : serie}, inplace=True)
        
        dataDf.append(data)
    
    main_df = dataDf[0]
    main_df = combine_dfs(main_df, dataDf[1:], xaxis_col)
    
    outxls = barchart_in_xls_from_df(main_df, outxls, series, xaxis_col)
    
    return outxls

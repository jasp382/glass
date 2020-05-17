"""
Collecting News from Journal Papers
"""


import argparse

"""
Parse Arguments using argparser
"""

def arg_parsing():
    
    parser = argparse.ArgumentParser(
        description="Collect Paper News related with extreme events from the Web"
    )
    
    parser.add_argument(
        '-s', '--search', action='store_true',
        help=(
            "Use this flag to search for news related with some words"
        )
    )
    
    parser.add_argument(
        '-wid', '--word_group_id', default=None, action='append',
        help=(
            "Usar esta se o objectivo for usar apenas um determinado "
            "grupo de palavras na realizacao das pesquisas. Esta opcao esta "
            "disponivel quando a flag -s esta a ser utilizada."
        )
    )
    
    # Add news table into database
    parser.add_argument('-nf', '--news_file', default=None, help=(
        "Use this flag to give a file with NEWS URL. This URL's will be "
        "imported to the database"
    ))
    
    parser.add_argument('-url', '--url_col', default=None, help=(
        "NAME URL col in --news-file"
    ))
    
    parser.add_argument('-grp', '--group_col', default=None, help=(
        "NAME GROUP Column in --news_file"
    ))
    
    parser.add_argument(
        '-sh', '--sheet_name', default=None, help=(
            'NAME Sheet with data in --news_file. Demandatory for ODS'
    ))
    
    parser.add_argument(
        '-jn', '--journal_col', default=None, help=(
            'Column name with Journal ID is demandatory when using --news_file '
            'flag.'
        )
    )
    
    return parser.parse_args()



def search_news_by_keyword(CON_PGSQL, SEARCH_WORDS, JOURNAL_TBL, NEWS_TBL,
                           GRP_ID=None):
    """
    Search for news using some words listed in one database
    and add it to database
    """
    
    import time
    from gasp             import goToList
    from glass.fm.psql     import query_to_df
    from glass.mng.gen     import merge_df
    from glass.sql.mng.tbl import rename_tbl, del_tables, row_num
    from glass.sql.mng.qw  import ntbl_by_query
    from glass.to.sql      import df_to_db
    from glass.web.search  import glg_search
    
    # Get Words
    GRP_ID = goToList(GRP_ID)
    wordsInterest = query_to_df(CON_PGSQL, "SELECT {}, {} FROM {}{}".format(
        SEARCH_WORDS["WORD"], SEARCH_WORDS["GROUP"], SEARCH_WORDS["TNAME"],
        "" if not GRP_ID else " WHERE {}".format(
            " OR ".join(["{}={}".format(
                SEARCH_WORDS["GROUP"], str(x)) for x in GRP_ID
            ])
        )
    )).to_dict(orient="index")
    
    # Get Journals
    journals = query_to_df(CON_PGSQL, "SELECT * FROM {}".format(
        JOURNAL_TBL["TNAME"]
    )).to_dict(orient="index")
    
    # Search for news using each keyword
    DFS_NEWS = []
    for w in wordsInterest:
        for j in journals:
            data = glg_search(
                str(wordsInterest[w][SEARCH_WORDS["WORD"]]),
                __site=str(journals[j][JOURNAL_TBL["URL"]]), NPAGES=10
            )
            
            data[NEWS_TBL["FK_JOURNAL"]] = journals[j][JOURNAL_TBL["PK"]]
            data[NEWS_TBL["WORD_GROUP"]] = wordsInterest[w][SEARCH_WORDS["GROUP"]]
            
            data.drop(["description", "name"], axis=1, inplace=True)
            
            # See if news URL has forbidden words
            for fburl in journals[j][JOURNAL_TBL["INVALID"]]:
                data["invalid"] = data['url'].str.contains(fburl)
                
                data = data[data["invalid"] == False]
                data.drop("invalid", axis=1, inplace=True)
            
            DFS_NEWS.append(data)
            
            time.sleep(10)
    
    df_news = merge_df(DFS_NEWS, ignIndex=True)
    
    # Update NEWS TABLE
    # Get last FID
    last_fid = query_to_df(CON_PGSQL, "SELECT MAX({f}) AS fid FROM {t}".format(
        f=NEWS_TBL["PK"], t=NEWS_TBL["TNAME"]
    )).iloc[0].fid
    
    df_news[NEWS_TBL["PK"]] = df_news.index + 1 + last_fid
    
    df_to_db(CON_PGSQL, df_news, NEWS_TBL["TNAME"], append=True, api='psql')
    
    # Erase duplicated news
    BEFORE_ROWS = row_num(CON_PGSQL, NEWS_TBL["TNAME"], api='psql')
    
    tmpNewsTbl = rename_tbl(CON_PGSQL, NEWS_TBL["TNAME"], NEWS_TBL["TNAME"] + "_tmp")
    
    ntbl_by_query(CON_PGSQL, NEWS_TBL["TNAME"], (
        "SELECT {idCol}, {urlCol}, {titleCol}, {wordCol}, {jornalId} "
        "FROM ("
            "SELECT *, row_number() OVER(PARTITION BY {urlCol} "
            "ORDER BY {idCol}) AS count_url FROM {tmpTbl}"
        ") AS foo WHERE count_url = 1 ORDER BY {idCol}"
    ).format(
        idCol=NEWS_TBL["PK"], urlCol=NEWS_TBL["URL"],
        titleCol=NEWS_TBL["TITLE"], wordCol=NEWS_TBL["WORD_GROUP"],
        jornalId=NEWS_TBL["FK_JOURNAL"], tmpTbl=tmpNewsTbl
    ))
    
    # del temporary table
    del_tables(CON_PGSQL, [tmpNewsTbl])
    
    AFTER_ROWS = row_num(CON_PGSQL, NEWS_TBL["TNAME"], api='psql')
    
    print "{} News were added to the dabtase".format(str(AFTER_ROWS - BEFORE_ROWS))


def from_news_get_text(CON_PGSQL, JOURNAL_TBL, NEWS_TBL, NEWS_PART):
    """
    Read a table with news URL and get the text of the news
    """
    
    import pandas
    from glass.fm.sql     import query_to_df
    from glass.web        import get_text_in_CssClass, get_text_in_html
    from glass.mng.gen    import merge_df
    from glass.sql.mng.qw import exec_write_q
    from glass.to.sql     import df_to_db
    from glass.sql.prop   import check_last_id
    
    """
    Obtain the URL's of the news to be collected
    """
    NEWS_TO_GET = query_to_df(CON_PGSQL, (
        "SELECT main.{}, main.{}, "
        "j.{}, j.{}, j.{} "
        "FROM {} AS main INNER JOIN {} AS j "
        "ON main.{} = j.{} "
        "WHERE {} IS NULL"
    ).format(
        NEWS_TBL["PK"], NEWS_TBL["URL"],
        JOURNAL_TBL["TAG_TITLE"], JOURNAL_TBL["TAG_CORPUS"],
        JOURNAL_TBL["CSS_CLASS"],
        NEWS_TBL["TNAME"], JOURNAL_TBL["TNAME"],
        NEWS_TBL["FK_JOURNAL"], JOURNAL_TBL["PK"],
        NEWS_TBL["TITLE"]
    ))
    
    # Check Shape
    if not NEWS_TO_GET.shape[0]:
        raise ValueError(
            'No news to get'
        )
    
    NEWS_DF = []
    TITLES  = {}
    
    def _news_text(row):
        fid        = row[NEWS_TBL["PK"]]
        url        = row[NEWS_TBL["URL"]]
        tag_title  = row[JOURNAL_TBL["TAG_TITLE"]]
        tag_corpus = row[JOURNAL_TBL["TAG_CORPUS"]]
        tag_css    = row[JOURNAL_TBL["CSS_CLASS"]]
        
        try:
            title = get_text_in_html(url, tags=[tag_title])
        except:
            TITLES[int(fid)] = "NO_ACCESS"
            return
        
        if not title[tag_title]:
            TITLES[int(fid)] = "NO_TITLE"
            return
        
        txtData = [get_text_in_CssClass(
            url, tag_corpus, csst
        ) for csst in tag_css]
        
        __txtData = []
        
        for t in txtData:
            if not t:
                continue
            
            __txtData += t['p']
        
        if not __txtData:
            TITLES[int(fid)] = "NO_TEXT"
            return
        
        new_text = pandas.DataFrame(__txtData, columns=[NEWS_PART["TEXT"]])
        new_text[NEWS_PART["NEWS"]] = fid
        new_text[NEWS_PART["PART"]] = new_text.index + 1
        
        TITLES[int(fid)] = title[tag_title][0]
        NEWS_DF.append(new_text)
    
    NEWS_TO_GET.apply(lambda x: _news_text(x), axis=1)
    
    if not NEWS_DF:
        print TITLES
        raise ValueError('Cannot any of the news text')
    
    APP_NEWS_TABLE = merge_df(NEWS_DF)
    
    APP_NEWS_TABLE[NEWS_PART["PART"]] = APP_NEWS_TABLE[NEWS_PART["PART"]].astype(int)
    
    # Update Titles Table
    UPDATE_QUERY = unicode((
        "UPDATE {tbl} SET {titleCol} = '{titleText}' "
        "WHERE {idCol} = {idNew}"
    ), 'utf-8')
    
    UPDATE_QUERIES = [UPDATE_QUERY.format(
        tbl=unicode(NEWS_TBL["TNAME"], 'utf-8'),
        titleCol=unicode(NEWS_TBL["TITLE"], 'utf-8'),
        titleText=TITLES[T].replace("'", ""),
        idCol=unicode(NEWS_TBL["PK"], 'utf-8'),
        idNew=unicode(str(T), 'utf-8')
    ) for T in TITLES]
    
    exec_write_q(CON_PGSQL, UPDATE_QUERIES)
    
    # Add news text to database
    # Check last row fid
    lastID = check_last_id(CON_PGSQL, NEWS_PART["ROW_ID"], NEWS_PART["TNAME"])
    APP_NEWS_TABLE[NEWS_PART["ROW_ID"]] = lastID + 1
    df_to_db(
        CON_PGSQL, APP_NEWS_TABLE, NEWS_PART["TNAME"],
        append=True, api='psql'
    )
    
    return NEWS_TBL["TNAME"]


def news_in_file_to_db(conPGSQL, NEWS_SCHEMA, file, url_col, word_grp_col,
                       journal_col, sheet=None):
    """
    Given a file with URLs, add this URLS in the database
    """
    
    from glass.to.db       import tbl_to_db
    from glass.pys.oss     import fprop
    from glass.sql.mng.qw  import ntbl_by_query
    from glass.sql.mng.tbl import rename_tbl, del_tables
    
    # Send file to Database to new table
    nTblNews = tbl_to_db(
        file, conPGSQL, fprop(file, 'fn'),
        sheet='news', api_db='psql'
    )
    
    # Rename old news_table
    rename_tbl(conPGSQL, NEWS_SCHEMA["TNAME"], "ttt_{}_ttt".format(
        NEWS_SCHEMA["TNAME"]))
    
    # Create a New Table with the old news and the new news
    nnTblNews = ntbl_by_query(conPGSQL, NEWS_SCHEMA["TNAME"], (
        "SELECT row_number() OVER (ORDER BY mtbl.{file_url}) + "
        "foo.max_fid AS {news_fid}, mtbl.{file_url} AS {news_url}, "
        "NULL AS {news_title}, mtbl.{file_grp} AS {news_grp}, "
        "mtbl.{file_jn} AS {news_jn} FROM ("
            "SELECT {file_url}, {file_grp}, {file_jn} "
            "FROM {t_file} GROUP BY {file_url}, {file_grp}, {file_jn}"
        ") AS mtbl LEFT JOIN {news_tbl} ON "
        "mtbl.{file_url} = {news_tbl}.{news_url}, ("
            "SELECT MAX({news_fid}) AS max_fid FROM {news_tbl}"
        ") AS foo WHERE {news_tbl}.{news_url} IS NULL "
        "UNION ALL SELECT * FROM {news_tbl}"
    ).format(
        file_url=url_col, file_grp=word_grp_col, file_jn=journal_col,
        t_file=nTblNews, news_tbl="ttt_{}_ttt".format(NEWS_SCHEMA["TNAME"]),
        news_fid=NEWS_SCHEMA["PK"], news_url=NEWS_SCHEMA["URL"],
        news_title=NEWS_SCHEMA["TITLE"], news_grp=NEWS_SCHEMA["WORD_GROUP"],
        news_jn=NEWS_SCHEMA["FK_JOURNAL"]
    ))
    
    # DEL temp table
    del_tables(conPGSQL, [
        "ttt_{}_ttt".format(NEWS_SCHEMA["TNAME"]),
        nTblNews
    ])


if __name__ == "__main__":
    """
    Run Script
    """
    
    args = arg_parsing()
    
    conDATABASE = {
        'HOST'     : 'localhost', 'USER' : 'postgres',
        'PASSWORD' : 'admin', 'PORT' : '5432',
        'DATABASE' : 'dsn_collect'
    }
    
    search_words = {
        "TNAME" : "search_words",
        "WORD"  : "word",
        "GROUP" : "group_id"
    }
    
    journal_tbl = {
        "TNAME"     : "jornais_web",
        "PK"        : "fid",
        "URL"       : "main_url",
        "TAG_TITLE" : "html_title",
        "TAG_CORPUS": "html_corpus",
        "CSS_CLASS" : "css_class",
        "INVALID"   : "forbidden"
    }

    news_table = {
        "TNAME"      : "noticias",
        "PK"         : "fid",
        "URL"        : "url",
        "TITLE"      : "titulo",
        "WORD_GROUP" : "word_grp",
        "FK_JOURNAL" : "jornal_fid"
    }
    
    news_parts = {
        "TNAME" : "noticias_parts",
        "ROW_ID": "fid",
        "PART"  : "news_part",
        "NEWS"  : "news_fid",
        "TEXT"  : "text"
    }
    
    if args.search:
        search_news_by_keyword(
            conDATABASE, search_words, journal_tbl, news_table,
            GRP_ID=args.word_group_id
        )
    
    elif args.news_file:
        if not args.url_col or not args.group_col:
            raise ValueError((
                "When using flag --news_file, --url_col and --group_col "
                "must be used also!"
            ))
        
        news_in_file_to_db(
            conDATABASE, news_table, args.news_file, args.url_col,
            args.group_col, args.journal_col, sheet=args.sheet_name
        )
    
    else:
        # Get text for news in News Table Table
        
        from_news_get_text(
            conDATABASE, journal_tbl, news_table, news_parts
        )


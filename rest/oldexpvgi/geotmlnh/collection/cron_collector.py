"""
Cron Collection of Digital Social Network data
"""

import argparse

"""
Parse Arguments using argparser
"""
def arg_parsing():
    parser = argparse.ArgumentParser(
        description='Cron Collectetion of data from DSN'
    )
    
    parser.add_argument(
        'source', help=(
            "Choose data source. Options are: facebook, twitter and flickr"
        )
    )
    
    return parser.parse_args()


"""
Facebook data collectors
"""
def fm_facebook(conPSQL, TABLE_SCHEMA):
    """
    Method to Get data from Facebook Daily
    
    Obsolete
    """
    
    import datetime;           import os; import time
    from glass.adv.dsn.fb.pages import extract_by_page
    from glass.sql.fm           import Q_to_df
    from glass.sql.mng.db       import create_db, dump_db
    from glass.sql              import run_sql_script
    from glass.sql.to           import df_to_db
    
    NPOSTS_TO_EXTRACT = 200
    
    LOG_LST = []
    
    # Create new database
    daytime = datetime.datetime.now().replace(microsecond=0)
    NEW_DATABASE = "fb_{}".format(str(daytime).replace('-', '').replace(
        ' ', '').replace(':', ''))
    
    create_db(conPSQL, NEW_DATABASE, overwrite=True)
    conPSQL["DATABASE"] = NEW_DATABASE
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    LOG_LST.append((
        time_a, 'DB with the name {} was created'.format(NEW_DATABASE)
    ))
    
    # Import DB template
    run_sql_script(conPSQL, conPSQL["DATABASE"], os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'db_collect.sql'
    ))
    
    time_b = datetime.datetime.now().replace(microsecond=0)
    LOG_LST.append((
        time_b, 'Table Schema was updated in {}'.format(NEW_DATABASE)
    ))
    
    # Get Facebook Pages with data to be collected
    PAGES = (conPSQL, (
        "SELECT {} FROM {}"
    ).format(
        TABLE_SCHEMA["NPAGE"], TABLE_SCHEMA["TPAGE"]
    ), db_api='psql')[TABLE_SCHEMA["NPAGE"]].tolist()
    
    # Extract data
    CONTA = 0
    error = None
    for page in PAGES:
        # Get data
        time_c = datetime.datetime.now().replace(microsecond=0)
        LOG_LST.append((
            time_c, 'Start collecting data from {} page'.format(page)
        ))
        
        dados = extract_by_page(page, 'posts', NPOSTS_TO_EXTRACT)
        
        if type(dados) == tuple:
            time_z = datetime.datetime.now().replace(microsecond=0)
            LOG_LST.append(
                time_z, 'Can not extract data from {}. That extraction failed!'.format(page)
            )
            
            error = True
            break
        
        time_d = datetime.datetime.now().replace(microsecond=0)
        LOG_LST.append((
            time_d, '{} posts were collect from {} page'.format(
                str(dados.shape[0]), page
            )
        ))
        
        df_to_db(
            conPSQL, dados, TABLE_SCHEMA["TDATA"],
            append=True, api='psql'
        )
        time_e = datetime.datetime.now().replace(microsecond=0)
        LOG_LST.append((
            time_e, 'Data from {} page is now in {}'.format(
                page, NEW_DATABASE
            )
        ))
        
        CONTA += 2
        
        if CONTA > 150:
            CONTA = 0
            time.sleep(3600)
        else:
            time.sleep(60)
    
    # Save database to file
    if not error:
        time_f = datetime.datetime.now().replace(microsecond=0)
        LOG_LST.append((
            time_f, 'Starting database dumping'
        ))
        dump_db(conPSQL, os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'dbs', '{}.sql'.format(
                conPSQL["DATABASE"]
            )
        ))
        time_g = datetime.datetime.now().replace(microsecond=0)
        LOG_LST.append((
            time_g, 'Database dumping is now complete'
        ))
    
    # Write log file
    LOG_TXT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'dbs', 'log_{}.txt'.format(
            conPSQL["DATABASE"]
        )
    )
    with open(LOG_TXT, 'w') as f:
        for lnh in LOG_LST:
            f.write("{}: {}\n".format(str(lnh[0]), lnh[1]))

"""
Twitter data collectors
"""
def fm_twitter(WORDS_TABLE, TABLE_DATA, PSQL_CON):
    """
    Get data from Twitter in a Cronjob
    """
    
    from multiprocessing   import Process
    import datetime;       import os; import time; import pandas
    from glass.sql.fm       import Q_to_df
    from glass.pys.df.split import split_df_inN
    from glass.adv.dsn.tw   import tweets_to_df
    from glass.pys.df.mng   import merge_df
    from glass.sql.to       import df_to_db
    
    
    
    
    
    # Know Day
    toDay = datetime.datetime.now().replace(microsecond=0).date()
    oneDay = toDay - datetime.timedelta(days=1)
    
    # Get keywords
    keywords = q_to_obj(PSQL_CON, "SELECT {} FROM {}".format(
        WORDS_TABLE["WORD"], WORDS_TABLE["TNAME"]
    ), db_api='psql')
    
    lst_keywords = split_df_inN(keywords, len(API_KEYS))
    
    DFS = []
    
    
    
    thrds = [Process(
        name="tk{}".format(str(i)), target=get_tweets,
        args=(lst_keywords[i], API_KEYS[i], i)
    ) for i in range(len(lst_keywords))]
    
    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()
    
    # Merge all dataframes
    if len(DFS) == 1:
        allDf = DFS[0]
    
    else:
        allDf = merge_df(DFS, ignIndex=True)
    
    allDf.rename(columns={"user" : "username"}, inplace=True)
    
    allDf = allDf[~allDf.fid.isin(ids[TABLE_DATA['FID']])]
    
    # Sanitize time reference
    allDf['daytime'] = pandas.to_datetime(allDf.tweet_time)
    allDf.daytime = allDf.daytime.astype(str)
    allDf.daytime = addDf.daytime.str.slice(start=0, stop=-6)
    allDf.drop('tweet_time', axis=1, inplace=True)
    
    # Rename cols
    allDf.rename(columns={
        'text' : 'txt', 'tweet_lang' : 'tlang', 'user_id' : 'userid',
        'user_location' : 'userloc', 'place_country' : 'placecountry',
        'place_countryc' : 'placecountryc', 'place_name' : 'placename',
        'place_box' : 'placebox', 'place_id' : 'placeid',
        'followers_count' : 'followersn'
    }, inplace=True)
    
    # Data to database
    tbl = df_to_db(PSQL_CON, allDf, TABLE_DATA["TNAME"], append=True, api='psql')
    
    time_c = datetime.datetime.now().replace(microsecond=0)
    LOG_LST.append((
        time_c, 'Starting database dumping'
    ))
    
    time_d = datetime.datetime.now().replace(microsecond=0)
    LOG_LST.append((
        time_d, 'Database dumping is now complete'
    ))
    
    # Write log file
    LOG_TXT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'dbs', 'log_{}.txt'.format(
            PSQL_CON["DATABASE"]
        )
    )
    with open(LOG_TXT, 'w') as f:
        for lnh in LOG_LST:
            f.write("{}: {}\n".format(str(lnh[0]), lnh[1]))


"""
Script initialization
"""
if __name__ == "__main__":
    args = arg_parsing()
    
    conPG = {
        'HOST'     : 'localhost', 'USER' : 'postgres',
        'PASSWORD' : 'admin', 'PORT' : '5432',
        'DATABASE' : 'expvgim_db'
    }
    
    if args.source == 'facebook':
        FACE_SCHEMA = {
            "TDATA" : "facedata",
            "TPAGE" : "face_pages",
            "NPAGE" : "page_name"
        }
        
        fm_facebook(conPG, FACE_SCHEMA)
    
    elif args.source == 'twitter':
        TWI_SCHEMA = {
            "TNAME" : "geotmlnh_words",
            "WORD"  : "word"
        }
        
        TWI_DATA = {
            "TNAME" : "geotmlnh_twitterdata",
            "FID"   : "fid",
            "TIME"  : "daytime"
        }
        
        fm_twitter(TWI_SCHEMA, TWI_DATA, conPG)
    
    else:
        raise ValueError("{} is not a valid value for source parameter")


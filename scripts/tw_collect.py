"""
Script to collect data from Twitter
"""

import argparse
import datetime as dt
import time

from glass.g.acq.dsn.tw import search_tweets

"""
Parse Arguments using argparser
"""
def arg_parsing():
    parser = argparse.ArgumentParser(
        description='Cron Collectetion of data from DSN'
    )
    
    parser.add_argument(
        '-kwg', '--keywordgroup', default=None,
        help=(
            "Choose keywords group. Options are: fire, etc and flickr"
        )
    )
    
    return parser.parse_args()


def get_tweets(DFSL, LOG, wdf, qareaparam, apik, drop_cols, ti):
    lk = wdf.word.tolist()

    if not ti:
        time_x = dt.datetime.now().replace(microsecond=0)
        LOG.append((
            "{} - Thread: 0 | "
            "Start searching for tweets without using Keyword"
        ).format(str(time_x)))

        a = search_tweets(
            keyword=None, in_geom=qareaparam, epsg=4326,
            NR_ITEMS=1000, resultType='mixed', key=apik,
            drop_cols=drop_cols
        )

        time_x = dt.datetime.now().replace(microsecond=0)

        if a.shape[0]:
            DFSL.append(a)

            LOG.append((
                "{} - Thread: 0 | "
                "{} Tweets were returned without using keyword"
            ).format(str(time_x), str(a.shape[0])))

            time.sleep(60)
            
        else:
            LOG.append("{} - Thread: 0 | 0 Tweets were returned".format(
                str(time_x)
            ))

    c = 1
    for kword in lk:
        time_z = dt.datetime.now().replace(microsecond=0)

        LOG.append("{} - Thread: {} | Searching using {} as keyword".format(
            str(time_z), str(ti), kword
        ))

        table = search_tweets(
            keyword=str(kword), in_geom=qareaparam, epsg=4326, NR_ITEMS=1000,
            resultType='mixed', key=apik, drop_cols=drop_cols
        )

        time_y = dt.datetime.now().replace(microsecond=0)

        if table.shape[0]:
            DFSL.append(table)

            LOG.append((
                "{} - Thread: {} | {} tweets "
                "were returned using {} as keyword"
            ).format(str(time_y), str(ti), str(table.shape[0]), kword))
            
        else:
            LOG.append((
                "{} - Thread: {} | 0 tweets "
                "were returned using {} as keyword"
            ).format(str(time_y), str(ti), kword))
            
        if c < len(lk):
            time.sleep(900)
            
        c += 1


def search_by_keyword(db, out_tbl, qarea, wgrp=None):
    """
    Get data using keywords
    """

    import os
    import pandas           as pd
    from multiprocessing    import Process, Manager
    from glass.cons.dsn     import search_words, tw_key
    from glass.ng.pd       import merge_df
    from glass.ng.pd.split import df_split
    from glass.g.wt.sql    import df_to_db

    # Get API Keys
    keys = tw_key()

    # Get search words
    words = search_words(group=wgrp)

    # Split search words
    search_words = [words] if len(keys) == 1 else df_split(words, len(keys))

    # Search for data
    with Manager() as manager:
        DFS       = manager.list()
        LOG_LST   = manager.list()
        DROP_COLS = ["retweeted"]
    
        # Create Threads
        thrds = [Process(
            name='tk{}'.format(str(i)), target=get_tweets,
            args=(DFS, LOG_LST, search_words[i], qarea, keys[i], DROP_COLS, i)
        ) for i in range(len(search_words))]

        for t in thrds:
            t.start()
    
        for t in thrds:
            t.join()
    
        if not len(DFS):
            raise ValueError('NoData was collected!')
    
        # Merge all dataframes
        if len(DFS) == 1:
            all_df = DFS[0]
    
        else:
            all_df = merge_df(DFS, ignIndex=True, ignoredfstype=True)
    
        all_df.rename(columns={"user" : "username"}, inplace=True)

        # Sanitize time reference
        all_df['daytime'] = pd.to_datetime(all_df.tweet_time)
        all_df.daytime = all_df.daytime.astype(str)
        all_df.daytime = all_df.daytime.str.slice(start=0, stop=-6)
        all_df.drop('tweet_time', axis=1, inplace=True)

        # Rename cols
        all_df.rename(columns={
            'text' : 'txt', 'tweet_lang' : 'tlang', 'user_id' : 'userid',
            'user_location' : 'userloc', 'place_country' : 'placecountry',
            'place_countryc' : 'placecountryc', 'place_name' : 'placename',
            'place_box' : 'placebox', 'place_id' : 'placeid',
            'followers_count' : 'followersn'
        }, inplace=True)

        # Data to new table
        df_to_db(db, all_df, out_tbl, append=True, api='psql')

        # Write log file
        log_txt = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '{}-log.txt'.format(out_tbl)
        )
        with open(log_txt, 'w') as f:
            f.write("\n".join(LOG_LST))
    
    return log_txt


if __name__ == "__main__":
    # Parameters
    args = arg_parsing()

    group = args.keywordgroup

    # Get search area
    search_area = {
        # Search in ALL Portugal Territory
        'x' : -(8 + (7/60.0) + (37.93 / 3600)),
        'y' : 39 + (42/60.0) + (3.41 / 3600),
        'r' : 300000
    }

    # Know Day
    day = str(dt.datetime.now().replace(microsecond=0).date()).replace('-', '')

    # DB to store data
    db = 'twitter2020'

    # Run collection script
    search_by_keyword(db, 'tw_' + day, search_area, wgrp=group)


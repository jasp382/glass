"""
Write logs in the database
"""

import os
import pandas as pd
import datetime as dt

from glass.wt.sql import df_to_db


def write_log(rsp, step, script, table, method, now, errormsg):
    """
    Write error log in the system log database
    """

    logs_db = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'fireloc_logs.sqlite'
    )

    logs_cols = [
        "step", "script", "status", "http",
        "description", "method", "code", "message",
        "start_time", "end_time"
    ]

    exphttp = 201 if method == 'POST' or method == 'PUT' else 200

    if rsp["status"] <= 0 or rsp["http"] != exphttp:
        # Write logs
        rd = rsp.get("json", None)

        end = dt.datetime.utcnow().replace(microsecond=0)

        log = [[
            step, script, rsp["status"], rsp["http"],
            errormsg, method,
            None if not rd else rd["status"]["code"],
            None if not rd else rd["status"]["message"],
            now.strftime('%Y-%m-%d %H:%M:%S'),
            end.strftime('%Y-%m-%d %H:%M:%S')
        ]]

        log_df = pd.DataFrame(log, columns=logs_cols)

        df_to_db(logs_db, log_df, table, append=True, api='sqlite')

        return 1
    
    return 0


def just_write_log(step, script, table, method, now, errormsg):
    """
    Write error log in the system log database
    """

    logs_db = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'fireloc_logs.sqlite'
    )

    logs_cols = [
        "step", "script", "status", "http",
        "description", "method", "code", "message",
        "start_time", "end_time"
    ]

    end = dt.datetime.utcnow().replace(microsecond=0)

    log = [[
        step, script, '', 0,
        errormsg, method,
        None, None,
        now.strftime('%Y-%m-%d %H:%M:%S'),
        end.strftime('%Y-%m-%d %H:%M:%S')
    ]]

    log_df = pd.DataFrame(log, columns=logs_cols)

    df_to_db(logs_db, log_df, table, append=True, api='sqlite')

    return 1


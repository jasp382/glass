"""
Set settings in the right places
"""

import os
import json as js
from glass.pys.oss  import del_file
from glass.ng.wt.js import dict_to_json


if __name__ == "__main__":
    # Get GIT Folder
    git_path = os.path.dirname(os.path.abspath(__file__))

    # Open settings file
    SETTINGS = js.load(open(os.path.join(
        git_path, 'settings.json'
    ), 'r'))

    # Create GLASS constants files
    # Add con-postgresql.json

    cpsql = os.path.join(
        git_path, 'core', 'glass', 'cons',
        'con-postgresql.json'
    )
    del_file(cpsql)

    dict_to_json({k : {
        "HOST"     : SETTINGS["POSTGRES"][k]["HOST"],
        "PORT"     : SETTINGS["POSTGRES"][k]["PORT"],
        "USER"     : SETTINGS["POSTGRES"][k]["USER"],
        "PASSWORD" : SETTINGS["POSTGRES"][k]["PASSWORD"],
        "TEMPLATE" : SETTINGS["POSTGRES"][k]["TEMPLATE"]
    } for k in SETTINGS["POSTGRES"]}, cpsql)

    # Add con-mysql.json
    cmsql = os.path.join(
        git_path, 'core', 'glass', 'cons',
        'con-mysql.json'
    )
    del_file(cmsql)

    dict_to_json({k : {
        "HOST"     : SETTINGS["MYSQL"][k]["HOST"],
        "PORT"     : SETTINGS["MYSQL"][k]["PORT"],
        "USER"     : SETTINGS["MYSQL"][k]["USER"],
        "PASSWORD" : SETTINGS["MYSQL"][k]["PASSWORD"]
    } for k in SETTINGS["MYSQL"]}, cmsql)
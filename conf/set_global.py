"""
Setup Global paramters

Applications:
- psql | PostgreSQL
- gsrv | GeoServer
"""

import argparse
import os
import json

from glass.pys.oss import del_file

def arg():
    """
    Script Arguments
    """

    parser = argparse.ArgumentParser(
        description="Create files with constant values"
    )

    parser.add_argument(
        '-a', '--app', default='psql',
        help='Type of constants'
    )

    parser.add_argument(
        '-H', '--host', default='localhost',
        help="Host name"
    )

    parser.add_argument(
        '-p', '--port', default='5432',
        help="Port"
    )

    parser.add_argument(
        '-P', '--password', default='admin',
        help='Password'
    )

    parser.add_argument(
        '-u', '--user', default='postgres',
        help='User name'
    )

    parser.add_argument(
        '-t', '--postgistemplate', default='postgis_template',
        help='Name of PostGIS Template Database'
    )

    return parser.parse_args()

if __name__ == '__main__':
    # Get Arguments
    args = arg()

    # Constants PATH
    conf_json = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'core', 'glass', 'cons'
    )

    # Get application
    app = args.app

    if app == 'psql':
        jf = os.path.join(conf_json, 'con-postgresql.json')

        # Delete file
        del_file(jf)

        # Write new configuration file
        with open(jf, 'w') as cf:
            json.dump({
                "default" : {
                    "HOST"     : args.host,
                    "USER"     : args.user,
                    "PORT"     : args.port,
                    "PASSWORD" : args.password,
                    "TEMPLATE" : args.postgistemplate
                }
            }, cf, indent=2)


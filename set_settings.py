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
        "HOST"     : SETTINGS["PSQL"][k]["HOST"],
        "PORT"     : SETTINGS["PSQL"][k]["PORT"],
        "USER"     : SETTINGS["PSQL"][k]["USER"],
        "PASSWORD" : SETTINGS["PSQL"][k]["PASSWORD"],
        "TEMPLATE" : SETTINGS["PSQL"][k]["TEMPLATE"]
    } for k in SETTINGS["PSQL"]}, cpsql)

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

    # Add con-geoserver.json
    cgsrv = os.path.join(
        git_path, 'core', 'glass', 'cons',
        'con-geoserver.json'
    )
    del_file(cgsrv)

    dict_to_json(SETTINGS["GEOSERVER"], cgsrv)

    # Add sentinel.json
    csentinel =  os.path.join(
        git_path, 'core', 'glass', 'cons',
        'sentinel.json'
    )
    del_file(csentinel)

    dict_to_json(SETTINGS["SENTINEL"], csentinel)

    # Create db container .env file
    env_db = os.path.join(
        git_path, 'docker', 'db', '.env'
    )
    del_file(env_db)

    dbc = SETTINGS["PSQL"]["default"]
    with open(env_db, 'w') as edb:
        edb.write((
            f"POSTGRES_DB={dbc['TEMPLATE']},{dbc['DATABASE']}\n"
            f"POSTGRES_USER={dbc['USER']}\n"
            f"POSTGRES_PASSWORD={dbc['PASSWORD']}\n"
            "ALLOW_IP_RANGE=0.0.0.0/0\n"
            "POSTGRES_MULTIPLE_EXTENSIONS=postgis,hstore,postgis_topology,postgis_raster,pgrouting\n"
            f"PGPASSWORD={dbc['PASSWORD']}"
        ))
    
    # Create db-backups .env file
    env_bk = os.path.join(
        git_path, 'docker', 'db', 'pg-backup',
        '.env'
    )
    del_file(env_bk)

    with open(env_bk, 'w') as bdb:
        bdb.write((
            "DUMPPREFIX=PG_db\n"
            f"POSTGRES_USER={dbc['USER']}\n"
            f"POSTGRES_PASS={dbc['PASSWORD']}\n"
            f"POSTGRES_PORT={dbc['DPORT']}\n"
            f"POSTGRES_HOST={dbc['DHOST']}\n"
            f"POSTGRES_DBNAME={dbc['DATABASE']}"
        ))
    
    # Create sdi container .env file
    env_sdi = os.path.join(
        git_path, 'docker', 'gsrv', '.env'
    )
    del_file(env_sdi)

    wehavessl = "true" if SETTINGS['GEOSERVER']['PROTOCOL'] \
        == 'https' else "false"
    
    with open(env_sdi, 'w') as esdi:
        esdi.write((
            "POSTGIS_VERSION_TAG=13.0\n"
            "GEOSERVER_VERSION_TAG=2.18.0\n"
            # Generic Env variables
            f"GEOSERVER_ADMIN_USER={SETTINGS['GEOSERVER']['USER']}\n"
            f"GEOSERVER_ADMIN_PASSWORD={SETTINGS['GEOSERVER']['PASSWORD']}\n"
            # https://docs.geoserver.org/latest/en/user/datadirectory/setting.html
            "GEOSERVER_DATA_DIR=/opt/geoserver/data_dir\n"
            # https://docs.geoserver.org/latest/en/user/data/raster/gdal.html#external-footprints-data-directory
            "GEOWEBCACHE_CACHE_DIR=/opt/geoserver/data_dir/gwc\n"
            # Show the tomcat manager in the browser
            "TOMCAT_EXTRAS=true\n"
            # https://docs.geoserver.org/stable/en/user/production/container.html#optimize-your-jvm
            "INITIAL_MEMORY=2G\n"
            # https://docs.geoserver.org/stable/en/user/production/container.html#optimize-your-jvm
            "MAXIMUM_MEMORY=4G\n"
            # https://docs.geoserver.org/stable/en/user/security/webadmin/csrf.html
            "GEOSERVER_CSRF_DISABLED=true\n"
            # Path where .ttf and otf font should be added
            "FONTS_DIR=/opt/fonts\n"
            # JVM Startup option for encoding
            "ENCODING='UTF8'\n"
            # JVM Startup option for timezone
            "TIMEZONE='GMT'\n"
            # DB backend to activate disk quota storage in PostgreSQL DB. Only permitted value is 'POSTGRES'
            "DB_BACKEND=\n"
            # https://docs.geoserver.org/latest/en/user/production/config.html#disable-the-auto-complete-on-web-administration-interface-login
            "LOGIN_STATUS=on\n"
            # https://docs.geoserver.org/latest/en/user/production/config.html#disable-the-geoserver-web-administration-interface
            "WEB_INTERFACE=false\n"
            # Rendering settings
            "ENABLE_JSONP=true \n"
            "MAX_FILTER_RULES=20 \n"
            "OPTIMIZE_LINE_WIDTH=false\n"
            # Install the stable plugin specified in https://github.com/kartoza/docker-geoserver/blob/master/build_data/stable_plugins.txt
            "STABLE_EXTENSIONS=\n"
            # Install the community edition plugins specified in https://github.com/kartoza/docker-geoserver/blob/master/build_data/community_plugins.txt
            "COMMUNITY_EXTENSIONS=\n"
            # SSL Settings explained here https://github.com/AtomGraph/letsencrypt-tomcat
            f"SSL={wehavessl}\n"
            "HTTP_PORT=8080 \n"
            "HTTP_PROXY_NAME=\n"
            "HTTP_PROXY_PORT= \n"
            "HTTP_REDIRECT_PORT= \n"
            "HTTP_CONNECTION_TIMEOUT=20000 \n"
            "HTTPS_PORT=8443\n"
            "HTTPS_MAX_THREADS=150\n"
            "HTTPS_CLIENT_AUTH=\n"
            "HTTPS_PROXY_NAME=\n"
            "HTTPS_PROXY_PORT=\n"
            "JKS_FILE=letsencrypt.jks\n"
            "JKS_KEY_PASSWORD='geoserver'\n"
            "KEY_ALIAS=letsencrypt\n"
            "JKS_STORE_PASSWORD='geoserver'\n"
            "P12_FILE=letsencrypt.p12\n"
            "PKCS12_PASSWORD='geoserver'\n"
            "LETSENCRYPT_CERT_DIR=/etc/letsencrypt\n"
            "CHARACTER_ENCODING='UTF-8'\n"
            # Clustering  variables
            # Activates clustering using JMS cluster plugin
            "CLUSTERING=False\n"
            # cluster env variables specified https://docs.geoserver.org/stable/en/user/community/jms-cluster/index.html
            "CLUSTER_DURABILITY=true\n"
            "BROKER_URL=\n"
            "READONLY=disabled\n"
            "RANDOMSTRING=23bd87cfa327d47e\n"
            "INSTANCE_STRING=ac3bcba2fa7d989678a01ef4facc4173010cd8b40d2e5f5a8d18d5f863ca976f\n"
            "TOGGLE_MASTER=true\n"
            "TOGGLE_SLAVE=true\n"
            "EMBEDDED_BROKER=enabled\n"
            # kartoza/postgis env variables https://github.com/kartoza/docker-postgis
            "POSTGRES_DB=gis,gwc\n"
            f"POSTGRES_USER={dbc['USER']}r\n"
            f"POSTGRES_PASS={dbc['PASSWORD']}\n"
            "ALLOW_IP_RANGE=0.0.0.0/0\n"
        ))


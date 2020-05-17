"""
Create GeoServer Layers
"""

from glass.sql.q         import q_to_obj
from glass.wg.gsrv.ws     import create_ws
from glass.wg.gsrv.stores import create_pgstore
from glass.wg.gsrv.lyrs   import pub_pglyr


if __name__ == '__main__':
    # Parameters
    data_db  = 'eow-db-contents'
    ghost_db = 'flainar-db-geoserver'

    ws = 'eowdeploy'
    store = 'ghost'

    # GeoServer Layers table
    gsrvlyr = 'geoserverlayers'

    setupdb = 'flainar'

    # Get Layers
    glyr = q_to_obj(
        data_db, "SELECT name FROM {}".format(gsrvlyr),
        dbset=setupdb
    )

    # Create workspace and store in GeoServer
    create_ws(ws, overwrite=True)
    create_pgstore(store, ws, ghost_db, dbset=setupdb + '-gsrv')

    # Create Layers in geoserver
    for idx, row in glyr.iterrows():
        pub_pglyr(ws, store, row['name'], title='tt_' + row['name'])


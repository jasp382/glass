def osm_vs_ndwis(shp, imds):
    import os
    import pandas as pd
    import numpy as np
    import glob

    from dgt.it.osm import osm_to_psql
    from dgt.it.shp import dbtbl_to_shp
    from dgt.wenv.grs import run_grass
    from dgt.dtt.torst import shp_to_rst
    from dgt.rd.shp import shp_to_obj
    from dgt.wt.shp import df_to_shp

    from dgt.prop.sql import cols_name
    from dgt.rd import tbl_to_obj
    from dgt.sql.q import exec_write_q
    from dgt.sql.db import create_db
    from dgt.pys.oss import mkdir, fprop
    
    # Prepare workspace
    ws = mkdir(os.path.join(
        os.path.dirname(shp), 'grswork'
    ), overwrite=True)
    
    results = mkdir(os.path.join(
            os.path.dirname(shp), 'results'
        ), overwrite=True)
    
    with open(f'{ws}/rulendwi.txt', 'w') as f:
        f.write('-1000 thru 100 = NULL\n100 thru 1000 = 1')

    with open(f'{ws}/rulendwi2.txt', 'w') as f:
        f.write('1 thru 10000 = 1')
        
    ndwitxt = (os.path.join(ws, 'rulendwi.txt'))
    ndwitxt2 = (os.path.join(ws, 'rulendwi2.txt'))
    
    imds = glob.glob(imds + '**.tif')
    
    a = 1
    
    for i in imds:
        
        result = mkdir(os.path.join(results, f'result{a}'
        ), overwrite=True)
        
        # Start GRASS GIS Session
        loc = f'locwork{a}'
        
        gb = run_grass(ws, location=loc, srs=i)

        import grass.script.setup as gsetup

        gsetup.init(gb, ws, loc, 'PERMANENT')

        # GRASS GIS Modules
        from dgt.it.shp import shp_to_grs, grs_to_shp
        from dgt.it.rst import rst_to_grs
        from dgt.gp.gen import dissolve
        from dgt.gp.ovl import grsintersection
        from dgt.smp import sample_to_points
        from grass.pygrass.modules import Module
        from dgt.it.rst import grs_to_rst
        
        # Import shp data
        watergrs = shp_to_grs(shp)

        imdgrs = rst_to_grs(i, fprop(i, 'fn'))

        Module ('r.mapcalc', expression = (f'imdgrs = {imdgrs} * 1000'))

        Module ('r.reclass', input = 'imdgrs', output = 'imdreclass',
                    rules = ndwitxt, title = 'imdreclass')

        Module('r.clump', input = 'imdreclass', output = 'imdclump', threshold=0, minsize=10)

        Module('r.reclass.area', input = 'imdclump', output = 'imdzonal',
                   mode='lesser', value=0.1, method='rmarea')

        Module ('r.reclass', input = 'imdzonal', output = 'zonalreclass',
                    rules = ndwitxt2, title = 'zonalreclass')

        Module('r.to.vect', input = 'zonalreclass', output = 'imdvect', type='area')

        Module('v.select', ainput= 'imdvect', binput='water', output='intersect', operator='overlap') 

        Module('v.select', ainput= 'imdvect', binput='water', output='crosses', operator='crosses') 

        #Module('v.select', ainput= 'imdvect', binput='water', output='contains', operator='contains')

        grs_to_rst('zonalreclass', os.path.join(result, 'ndwizonal.tif'))

        grs_to_shp('intersect', os.path.join(result, 'intersect.shp'), 'area')

        grs_to_shp('crosses', os.path.join(result, 'crosses.shp'), 'area')

        #grs_to_shp('contains', os.path.join(result, 'contains.shp'), 'area')
        
        a = a + 1
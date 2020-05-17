"""
Run ESRI Service Areas
"""

if __name__ == '__main__':
    import os
    from glass.g.mob.esri import service_areas

    folder = '/home/jasp/mrgis/gigs'

    d = [{
        "f"      : 'centrosdia.shp',
        "breaks" : ['5'],
        "output" : 'sa_cdia_5min.shp'
    }, {
        "f"      : 'centrosdia.shp',
        "breaks" : ['15'],
        "output" : 'sa_cdia_15min.shp'
    }, {
        "f"      : 'centrosdia.shp',
        "breaks" : ['30'],
        "output" : 'sa_cdia_30min.shp'
    },{
        "f"      : 'creches_nd.shp',
        "breaks" : ['5'],
        "output" : 'sa_creche_5min.shp'
    }, {
        "f"      : 'creches_nd.shp',
        "breaks" : ['15'],
        "output" : 'sa_creche_15min.shp'
    },{
        "f"      : 'creches_nd.shp',
        "breaks" : ['30'],
        "output" : 'sa_creche_30min.shp'
    },{
        "f"      : 'Equipamentos_Desportivos.shp',
        "breaks" : ['5'],
        "output" : 'sa_desp_5min.shp'
    }, {
        "f"      : 'Equipamentos_Desportivos.shp',
        "breaks" : ['15'],
        "output" : 'sa_desp_15min.shp'
    }, {
        "f"      : 'Equipamentos_Desportivos.shp',
        "breaks" : ['30'],
        "output" : 'sa_desp_30min.shp'
    }]

    impedance = 'WalkTime'
    
    for i in d:
        service_areas(
            os.path.join(folder, i['f']),
            i['breaks'],
            os.path.join(folder, i["output"]),
            impedance=impedance
        )


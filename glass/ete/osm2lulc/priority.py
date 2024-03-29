"""
Priority rule implementation
"""


def priority_rule(osmshps, priorities, gis_software, db=None):
    """
    Priority rule in Arcgis
    """
    
    import copy; import os
    if gis_software != 'psql':
        from glass.gp.ovl import erase
    else:
        from glass.gp.ovl.sql import st_erase
    from glass.pys.oss import fprop
    
    osmNameRef = copy.deepcopy(osmshps)
    
    for e in range(len(priorities)):
        if e + 1 == len(priorities): break
        
        if priorities[e] not in osmshps:
            continue
        
        else:
            for i in range(e+1, len(priorities)):
                if priorities[i] not in osmshps:
                    continue
                
                else:
                    if gis_software == 'arcpy':
                        tmpOut = os.path.join(
                            os.path.dirname(osmshps[priorities[i]]),
                            f"{fprop(osmNameRef[priorities[i]], 'fn')}_{e}.shp"
                        )
                    
                    else:
                        tmpOut = f"{osmNameRef[priorities[i]]}_{e}"
                    
                    if gis_software == 'psql':
                        osmshps[priorities[i]] = st_erase(
                            db, osmshps[priorities[i]],
                            osmshps[priorities[e]], 'geom', 'geom',
                            tmpOut
                        )
                    
                    else:  
                        osmshps[priorities[i]] = erase(
                            osmshps[priorities[i]], osmshps[priorities[e]],
                            tmpOut, api=gis_software
                        )
    
    return osmshps


"""
Extraction Operations using OSM Data
"""


def highways_from_osm(inOsm, outOsm, filter_geom=None, api='osmosis'):
    """
    Extract highways from one OSM file

    api options:
    * osmosis;
    * osmconvert;
    """
    
    import os
    from glass.pys import execmd
    
    if api == 'osmosis':
        outExt = os.path.splitext(outOsm)[1]

        ext = "pbf" if outExt == ".pbf" else "xml"
    
        cmd = (
            f'osmosis --read-xml enableDateParsing=no file={inOsm} '
            '--tf accept-ways '
            f'highway=* --used-node --write-{ext} {outOsm}' 
        )
    
    elif api == 'osmconvert':
        if filter_geom:
            # Get shape extent
            from glass.prop.ext import get_ext

            dataext = get_ext(filter_geom, outEpsg=4326)

            bbox = (
                f" -b={str(dataext[0])},{str(dataext[2])},"
                f"{str(dataext[1])},{str(dataext[3])}"
            )
        
        else:
            bbox = ''
        
        cmd = f"osmconvert {inOsm}{bbox} --complete-ways -o={outOsm}"
    
    else:
        raise ValueError(f"{api} API is not available!")
    
    outcmd = execmd(cmd)
    
    return outOsm

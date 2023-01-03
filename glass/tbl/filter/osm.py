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
    
        cmd = (
            'osmosis --read-xml enableDateParsing=no file={} --tf accept-ways '
            'highway=* --used-node --write-{} {}' 
        ).format(
            inOsm,
            "pbf" if outExt == ".pbf" else "xml", outOsm
        )
    
    elif api == 'osmconvert':
        if filter_geom:
            # Get shape extent
            from glass.prop.ext import get_ext

            dataext = get_ext(filter_geom, outEpsg=4326)
        
        else:
            dataext = None
        
        cmd = "osmconvert {}{} --complete-ways -o={}".format(
            inOsm, "" if not dataext else " -b={},{},{},{}".format(
                str(dataext[0]), str(dataext[2]),
                str(dataext[1]), str(dataext[3])
            ), outOsm
        )
    
    else:
        raise ValueError(f"{api} API is not available!")
    
    outcmd = execmd(cmd)
    
    return outOsm

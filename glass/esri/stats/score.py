"""
Methods to normalize variables using Arcpy
"""

import arcpy


def range_score(raster, output, MAX=True, __template=None):
    """
    Calculate a Range Score of a Raster
    
    If Max, major values will be the major values in the normalized raster;
    Else, major values will be the minor values in the normalizes raster.
    """
    
    from glass.pys.oss         import fprop
    from glass.esri.rd.rst          import rst_to_lyr
    from glass.prop.rst        import rst_stats
    from glass.spanlst.algebra import rstcalc
    
    lyr = rst_to_lyr(raster)
    
    __max = rst_stats(lyr, api='arcpy')["MAX"]
    __min = rst_stats(lyr, api='arcpy')["MIN"]
    
    express = '({rst} - {_min}) / ({_max} - {_min})' if MAX else \
        '({_max} - {rst}) / ({_max} - {_min})'
    
    rstcalc(
        express.format(
            _min=str(__min), _max=str(__max),
            rst=fprop(raster, 'fn')
        ),
        output, api='arcpy'
    )
    
    return output


def maximum_score(raster, output, MAX=True, __template=None):
    """
    Calculate a Maximum Score of a Raster
    
    If Max, major values will be the major values in the normalized raster;
    Else, major values will be the minor values in the normalizes raster.
    """
    
    from glass.pys.oss         import fprop
    from glass.esri.rd.rst     import rst_to_lyr
    from glass.prop.rst        import rst_stats
    from glass.spanlst.algebra import rstcalc
    
    lyr = rst_to_lyr(raster)
    
    __max = rst_stats(lyr, api='arcpy')["MAX"]
    
    express = '{rst} / {_max}' if MAX else '1 - ({rst} / {_max})'
    
    rstcalc(express.format(
        rst=fprop(raster, 'fn'), _max=str(__max)
    ), output, template=__template, api='arcpy')
    
    return output


"""
Sampling ArcGIS tools
"""

import arcpy
import os


def ag_split_rst_randomly(inrst, proportion, random_rst, other_rst, min_sample=None):
    """
    Extract some cells of one raster and save them into a new raster

    The cells not selected for extraction will be exported to other raster.
    """

    from glass.esri.rd.rst import ag_rst_to_refarray
    from glass.esri.prop.rst import rst_geoprop
    from glass.pys.sampling import split_binparray_randomly
    from glass.esri.wt import obj_to_rst

    # Get raster geoproperties
    lfeft, csize = rst_geoprop(inrst)

    # Read raster
    rnum, nd, rshp = ag_rst_to_refarray(inrst, rshp='flatten', rmnd=None)

    # Select cells randomly
    sel, nsel = split_binparray_randomly(
        rnum, nd, rshp, proportion, min_sample=min_sample
    )

    obj_to_rst(sel, random_rst, lfeft, csize, nd)
    obj_to_rst(nsel, other_rst, lfeft, csize, nd)

    return random_rst, other_rst


def rnd_points(rndPntShp, NPoints, whereShp, distTolerance=None):
    """
    Create NRandom Points inside some area
    and save the result in one file
    """
    
    import os
    from glass.pys.oss import fprop
    
    distT = "" if not distTolerance else f"{distTolerance} Meters"
    
    arcpy.CreateRandomPoints_management(
        os.path.dirname(rndPntShp),
        fprop(rndPntShp, 'fn'), whereShp,
        "", NPoints, distT, "POINT", "0"
    )
    
    return rndPntShp


def rnd_points_with_dist_from_points(otherPnt, rndPnt, NPnt,
                                     distFromOtherPnt, boundary,
                                     distRndTolerance=None):
    """
    Create NRandom Points with a distance of X from other Points
    """
    
    from glass.pys.oss import fprop
    from gesri.gp.ovl  import erase
    from gesri.gp.prox import _buffer
    
    WORKSPACE = os.path.dirname(rndPnt)
    
    # Create Buffer
    bfShp = _buffer(
        otherPnt, distFromOtherPnt, os.path.join(
            WORKSPACE,
            f"{fprop(otherPnt, 'fn')}_buffer.shp"
        ),
        dissolve="ALL", api='arcpy'
    )
    
    # Erase Boundary deleting areas where we want no points
    erased = erase(
        boundary, bfShp, 
        os.path.join(
            WORKSPACE,
            f"{fprop(boundary, 'fn')}_erase.shp"
        )
    )
    
    # Create Random Points
    return rnd_points(
        rndPnt, NPnt, erased,
        distTolerance=distRndTolerance
    )


def fishnet(output, templateExtent, geomType='POLYGON',
            numRows=None, numColumns=None,
            cellWidth=None, cellHeight=None,
            labeling="NO_LABELS"):
    """
    Create a fishnet - rectangular cells
    
    Use fc or raster to assign a extent to the new fishnet
    """
    
    from glass.prop.ext import rst_ext, get_extent
    from glass.prop.df  import vector_formats, raster_formats
    from glass.pys.oss  import fprop
    
    templateFormat = fprop(templateExtent, 'ff')
    
    if templateFormat in vector_formats():
        xmin, xmax, ymin, ymax = get_extent(templateExtent, gisApi='arcpy')
    elif templateFormat in raster_formats():
        xmin, xmax, ymin, ymax = rst_ext(templateExtent, gisApi='arcpy')
    
    else:
        raise ValueError(('Could not identify if observerDataset '
                          'is a raster or a feature class'))
    
    arcpy.CreateFishnet_management(
        out_feature_class=output,
        origin_coord=' '.join([str(xmin), str(ymin)]),
        y_axis_coord=' '.join([str(xmin), str(ymin + 10.0)]),
        cell_width=cellWidth, 
        cell_height=cellHeight, 
        number_rows=numRows, 
        number_columns=numColumns,
        labels=labeling, 
        template=templateExtent, 
        geometry_type=geomType
    )
    
    return output

